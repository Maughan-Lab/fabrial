from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from abc import abstractmethod
from asyncio import CancelledError
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Iterable, Protocol

from ..classes import FatalSequenceError, PlotHandle, PlotIndex, PlotSettings
from ..constants.paths.sequence import METADATA_FILENAME

if TYPE_CHECKING:
    from ..tabs import SequenceDisplayTab


# don't sort
import asyncio
import copy
from asyncio import CancelledError, Task, TaskGroup
from enum import Enum, auto
from queue import Empty, Queue

from PyQt6.QtCore import QThread, pyqtSignal

from ..classes import DataLock


class SequenceStatus(Enum):
    """Statuses for the sequence."""

    Active = auto()
    Paused = auto()
    Completed = auto()
    Cancelled = auto()
    FatalError = auto()


class SequenceCommand(Enum):
    """Commands that can be send to the sequence thread."""

    Pause = auto()
    Unpause = auto()
    Cancel = auto()


class SequenceThread(QThread):
    """A `QThread` where the sequence runs."""

    statusChanged = pyqtSignal(SequenceStatus)
    # title, message, options, response receiver
    promptRequested = pyqtSignal(str, str, dict, DataLock)
    plotCommandRequested = pyqtSignal(object)  # the plot command (a function)
    stepStateChanged = pyqtSignal(int, bool)  # step address, whether the step is being run

    # overridden
    def __init__(
        self,
        steps: Iterable[SequenceStep],
        data_directory: Path,
        command_queue: Queue[SequenceCommand],
    ):
        QThread.__init__(self)
        self.steps = steps
        self.data_directory = data_directory
        self.command_queue = command_queue

    def run(self):  # overridden
        try:
            self.statusChanged.emit(SequenceStatus.Active)
            runner = StepRunner()
            cancelled = asyncio.run(self.run_actual(runner))
            self.statusChanged.emit(
                SequenceStatus.Cancelled if cancelled else SequenceStatus.Completed
            )
        except (FatalSequenceError, Exception):
            logging.getLogger(__name__).exception("Sequence raised a fatal exception")
            self.statusChanged.emit(SequenceStatus.FatalError)

    async def run_actual(self, runner: StepRunner) -> bool:
        """
        The actual run function (required so we can do `asyncio.run()`). Returns whether the
        sequence ended normally. This can raise exceptions.
        """
        async with TaskGroup() as task_group:
            sequence_task = task_group.create_task(
                runner.run_steps(self.steps, self.data_directory)
            )
            monitor_task = task_group.create_task(self.monitor(runner))
            # if either task ends, cancel the other
            monitor_task.add_done_callback(lambda _: sequence_task.cancel())
            sequence_task.add_done_callback(lambda _: monitor_task.cancel())
        return not sequence_task.cancelled()

    async def monitor(self, runner: StepRunner) -> None:
        """Monitor for messages and commands."""
        while True:
            self.check_commands()
            self.check_runner(runner)
            await asyncio.sleep(0)

    def check_commands(self):
        """Check for commands and process them."""
        try:
            while True:
                command = self.command_queue.get_nowait()
                match command:
                    case SequenceCommand.Pause:
                        self.pause()
                    case SequenceCommand.Cancel:
                        raise CancelledError
                    case SequenceCommand.Unpause:  # this should never run
                        raise ValueError(
                            "Received `SequenceStep.Unpause`, which should be impossible"
                        )
        except Empty:
            pass

    def pause(self):
        """Pause the sequence."""
        while True:
            try:
                command = self.command_queue.get_nowait()
                match command:
                    case SequenceCommand.Cancel:
                        raise CancelledError
                    case SequenceCommand.Unpause:
                        return
                    case SequenceCommand.Pause:  # ignore additional pauses
                        pass
            except Empty:
                pass
            time.sleep(0)  # this is not `asyncio.sleep()`

    def check_runner(self, runner: StepRunner):
        """Check the `StepRunner` for any messages to pass on."""
        # forward any prompt requests
        for _ in range(len(runner.prompt_requests)):
            self.promptRequested.emit(*runner.prompt_requests.pop())
        # forward any plot commands
        for _ in range(len(runner.plot_commands)):
            self.plotCommandRequested.emit(runner.plot_commands.pop())
        # notify of any steps starting or stopping
        for _ in range(len(runner.step_info)):
            self.stepStateChanged.emit(*runner.step_info.pop())


class StepRunner:
    """Runs `SequenceStep`s and provides utility functions that steps can call."""

    def __init__(self):
        # send prompts to the user
        self.prompt_requests: deque[tuple[str, str, dict[int, str], DataLock[int | None]]] = deque()
        # holds commands to send the the visuals tab
        self.plot_commands: deque[Callable[[SequenceDisplayTab], None]] = deque()
        # holds information about steps starting and finishing
        self.step_info: deque[tuple[int, bool]] = deque()

    async def run_steps(self, steps: Iterable[SequenceStep], data_directory: Path):
        """Run the provided **steps** sequentially. This can be called by `SequenceStep`s."""
        for i, step in enumerate(steps):
            step_address = id(step)
            # create the data directory first
            step_data_directory = await self.make_step_directory(data_directory, i, step)
            # run the step
            self.step_info.appendleft((step_address, True))  # notify start
            try:
                await self.run_single_step(step, step_data_directory)
            finally:
                self.step_info.appendleft((step_address, False))  # notify finish

    async def run_single_step(self, step: SequenceStep, step_data_directory: Path):
        """
        Run a single sequence step.

        Raises
        ------
        CancelledError
            The sequence was cancelled.
        FatalSequenceError
            The sequence encountered a fatal error.
        """
        cancelled = False
        error_occurred = False
        start_datetime = datetime.now()  # record step start time
        try:
            await step.run(self, step_data_directory)
        except FatalSequenceError:  # fatal errors are not recoverable
            # intentionally putting this code here far clarity
            # we don't log metadata for fatal errors
            raise
        except CancelledError:  # log cancellation then cancel
            cancelled = True
            await self.record_metadata(
                step_data_directory, step, start_datetime, cancelled, error_occurred
            )
            raise
        except Exception:  # recoverable error; log and ask the user what to do
            logging.getLogger(__name__).exception("Sequence step error")

            error_occurred = True
            # update the cancelled variable
            cancelled = not await self.prompt_handle_error(
                step, f"The current step, {step.name()}, encountered an error."
            )
            if cancelled or not await self.record_metadata(
                step_data_directory, step, start_datetime, cancelled, error_occurred
            ):
                raise CancelledError  # actually cancel

    async def make_step_directory(
        self, data_directory: Path, number: int, step: SequenceStep
    ) -> Path:
        """
        Create the data directory for **step** and return the directory's path.

        Raises
        ------
        CancelledError
            The sequence was cancelled.
        FatalSequenceError
            The sequence encountered a fatal error.
        """
        step_data_directory = data_directory.joinpath(f"{number} {step.directory_name()}")
        try:
            os.makedirs(step_data_directory, exist_ok=True)
        except OSError:
            if not await self.prompt_handle_error(
                step, f"Failed to create data directory {step_data_directory}"
            ):
                raise CancelledError
        return step_data_directory

    async def prompt_user(self, step: SequenceStep, message: str, options: dict[int, str]) -> int:
        """
        Show a popup prompt to the user and wait for a response. This can be called by
        `SequenceStep`s.

        Parameters
        ----------
        step
            The `SequenceStep` requesting the prompt.
        message
            The prompt's text.
        options
            A mapping of values to options in the prompt. For example,
            `{1: "First Option", 2: "Second Option}` will show a prompt with options "First Option"
            and "Second Option". If the user selects "First Option", this function will return `1`.
            If the user selects "Second Option", this function will return `2`.
        """
        return await self.send_prompt_and_wait(
            f"Sequence: Message From {step.name()}", message, options
        )

    async def prompt_handle_error(self, step: SequenceStep, error_message: str) -> bool:
        """
        Ask the user how to handle a sequence step encountering an error.

        Returns
        -------
        Whether the sequence should continue.

        Raises
        ------
        FatalSequenceError
            An invalid response was sent (this indicates an issue with the core codebase).
        """
        response = await self.send_prompt_and_wait(
            f"Sequence: Error in {step.name()}",
            f"{error_message}\n\nnSkip current step or cancel the sequence?",
            {0: "Skip Current", 1: "Cancel"},
        )
        match response:
            case 0:  # skip current
                return True
            case 1:  # cancel
                return False
            case _:  # this should never run
                raise FatalSequenceError(f"Reponse was {response} when it should have been 0 or 1")

    async def send_prompt_and_wait(self, title: str, message: str, options: dict[int, str]) -> int:
        """Private helper function to send a message the the user and wait for a response."""
        receiver: DataLock[int | None] = DataLock(None)
        self.prompt_requests.appendleft((title, message, options, receiver))  # request a prompt
        # wait for the response
        while True:
            await asyncio.sleep(0)
            if (response := receiver.get()) is not None:
                return response

    async def record_metadata(
        self,
        directory: Path,
        step: SequenceStep,
        start_datetime: datetime,
        cancelled: bool,
        error_occurred: bool,
    ) -> bool:
        """
        Generate the default metadata and combine it with the **step**'s metadata, then write the
        data to a metadata file in the **step**'s data directory.

        Returns
        -------
        Whether the sequence should continue.

        Raises
        ------
        FatalSequenceError
            The sequence encountered a fatal error.
        """
        try:
            file = directory.joinpath(METADATA_FILENAME)
            data = step.metadata()
            # we do it in this order so the step's metadata gets overridden if there are duplicate
            # keys. The default keys are reserved
            data.update(
                {
                    "Start Datetime": str(start_datetime),
                    "End Datetime": str(datetime.now()),
                    "Cancelled": cancelled,
                    "Error": error_occurred,
                }
            )
            with open(file, "w") as f:
                json.dump(data, f)
        except Exception:
            logging.getLogger(__name__).exception("Failed to write metadata")
            return await self.prompt_handle_error(
                step, "Failed to record metadata for the current step."
            )
        return True

    async def create_plot(
        self, step: SequenceStep, tab_text: str, plot_settings: PlotSettings
    ) -> PlotHandle:
        """
        Create a new plot on the visuals tab and return a handle to it. This waits until the plot
        is created. This can be called by `SequenceStep`s.

        Parameters
        ----------
        step
            The step creating the plot (generally just pass `self`).
        tab_text
            The text of the plot's tab.
        plot_settings
            The `PlotSettings` to configure the new plot with.

        Returns
        -------
        A thread-safe handle for the plot that can be used to modify it from your `SequenceStep`.
        """
        receiver: DataLock[PlotIndex | None] = DataLock(None)
        step_address = id(step)  # copy
        step_name = step.name()  # copy
        # notify that we want to create a new plot
        self.submit_plot_command(
            lambda plot_tab: plot_tab.add_plot(
                step_address, step_name, tab_text, plot_settings, receiver
            )
        )
        # wait for a response
        while True:
            await asyncio.sleep(0)
            if (plot_index := receiver.get()) is not None:
                return PlotHandle(self, plot_index)  # return the plot handle

    # used externally
    def submit_plot_command(self, command: Callable[[SequenceDisplayTab], None]):
        """
        Submit a **command** to the plot command queue. This is not for direct use by
        `SequenceStep`s.
        """
        self.plot_commands.appendleft(command)


class SequenceStep(Protocol):
    """Represents a sequence step that the sequence can run."""

    @abstractmethod
    async def run(self, runner: StepRunner, data_directory: Path):
        """
        Run the sequence step. Ensure you call `self.sleep()` often enough that other tasks can be
        run.
        """
        ...

    @abstractmethod
    def reset(self):
        """
        Reset this step to its original state (i.e. before `run()` was called). Sequence steps might
        be re-used, so they must be resettable. An easy implementation is to call `__init__()` to
        reinitialize with the original parameters.
        """
        ...

    @abstractmethod
    def name(self) -> str:
        """A name used to represent this step. For example, "Hold" or "Increment Temperature"."""
        ...

    @abstractmethod
    def directory_name(self) -> str:
        """Get the name (i.e. not full path) of the directory where data should be recorded."""
        ...

    def metadata(self) -> dict[str, Any]:
        """Get metadata for this sequence step to be recorded in a JSON file."""
        return {}

    async def sleep(self, delay: float):
        """
        Sleep this sequence step for **delay** seconds. This is *not* equivalent to `time.sleep()`
        and should be used *instead* of `time.sleep()`.
        """
        await asyncio.sleep(delay)

    async def sleep_until(self, when: float):
        """Sleep until **when**, which is a `float` as returned by `time.time()`."""
        await self.sleep(0)  # make sure we sleep at all
        await self.sleep(when - time.time())
