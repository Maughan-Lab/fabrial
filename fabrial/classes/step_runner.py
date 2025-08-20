from __future__ import annotations

import asyncio
import contextlib
import copy
import json
import logging
import os
from asyncio import CancelledError
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, AsyncGenerator, Callable, Iterable

from PyQt6.QtCore import QObject, pyqtSignal

from ..constants.paths.sequence import METADATA_FILENAME
from ..plotting import PlotHandle, PlotIndex, PlotSettings
from .exceptions import FatalSequenceError
from .lock import DataLock
from .sequence_step import SequenceStep

if TYPE_CHECKING:
    from ..tabs import SequenceDisplayTab


class StepRunner(QObject):
    """Runs `SequenceStep`s and provides utility functions that steps can call."""

    # title, message, options, response receiver
    promptRequested = pyqtSignal(str, str, dict, DataLock)
    """
    Emitted when a prompt needs to be sent the the main thread.

    Sends
    -----
    - The prompt title as a `str`.
    - The prompt text as a `str`.
    - The prompt options as a `dict[int, str]`.
    - The receiver as a `DataLock[int | None]`.
    """
    plotCommandRequested = pyqtSignal(object)
    """
    Emitted when a plot command needs to be run.

    Sends
    -----
    - The plot command as a `Callable[SequenceDisplayTab]`.
    """
    # the first argument is `qint64` because using `int` constrains it to 32 bits
    stepStateChanged = pyqtSignal("qint64", bool)
    """
    Emitted when a step is started/finished.

    Sends
    -----
    - The step's memory address as an `int`.
    - `True` if the step was started, `False` if it was finished (`bool`).
    """

    # ----------------------------------------------------------------------------------------------
    # public
    def __init__(self):
        QObject.__init__(self)

    async def run_steps(self, steps: Iterable[SequenceStep], data_directory: Path):
        """
        Run the provided steps sequentially. This can be called by `SequenceStep`s.

        Parameters
        ----------
        steps
            The steps to run.
        data_directory
            The base directory to put the steps' data directories in.

        Raises
        ------
        See `run_single_step()`.
        """
        for i, step in enumerate(steps):
            await self.run_single_step(step, data_directory, i + 1)  # run the step

    async def run_single_step(self, step: SequenceStep, data_directory: Path, step_number: int):
        """
        Run a single sequence step. This can be called by `SequenceStep`s.

        Parameters
        ----------
        step
            The `SequenceStep` to run.
        data_directory
            The base directory to put the step's data directory in.
        step_number
            The step's number (currently used to prefix the step's data directory).

        Raises
        ------
        CancelledError
            The sequence was cancelled.
        FatalSequenceError
            The sequence encountered a fatal error.

        Do not suppress these errors.
        """
        step_address = id(step)  # get the address
        # create the data directory first
        step_data_directory = await self.make_step_directory(data_directory, step, step_number)
        self.stepStateChanged.emit(step_address, True)  # notify start

        cancelled = False
        error_occurred = False
        start_datetime = datetime.now()  # record step start time
        try:
            try:
                await step.run(self, step_data_directory)
            except FatalSequenceError:  # fatal errors are not recoverable
                # intentionally putting this code here far clarity
                # we don't log metadata for fatal errors
                raise
            except Exception:  # recoverable error; log and ask the user what to do
                logging.getLogger(__name__).exception("Sequence step error")

                error_occurred = True
                # update the cancelled variable
                await self.prompt_handle_error(
                    step, f"The current step, {step.name()}, encountered an error."
                )
        except CancelledError:  # log cancellation then cancel
            cancelled = True
            await self.record_metadata(
                step_data_directory, step, start_datetime, cancelled, error_occurred
            )
            raise
        finally:
            self.stepStateChanged.emit(step_address, False)  # notify finish
        # this runs if there wasn't a fatal error and the sequence wasn't cancelled
        await self.record_metadata(
            step_data_directory, step, start_datetime, cancelled, error_occurred
        )

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

    async def prompt_retry_cancel(self, step: SequenceStep, message: str) -> bool:
        """
        Ask the user whether the **step** should retry something or cancel. This can be called by
        `SequenceStep`s.

        Parameters
        ----------
        step
            The `SequenceStep` requesting the prompt.
        message
            The prompt's text, excluding the part about retrying or canceling.

        Returns
        -------
        `True` if the operation should be retried, `False` if the step should cancel.
        """
        match (
            response := await self.prompt_user(
                step, f"{message}\n\nRetry or cancel the step?", {0: "Retry", 1: "Cancel Step"}
            )
        ):
            case 0:  # retry
                return True
            case 1:  # cancel step
                return False
            case _:
                raise FatalSequenceError(f"Got {response} but expected 0 or 1")

    @contextlib.asynccontextmanager
    async def create_plot(
        self, step: SequenceStep, tab_text: str, plot_settings: PlotSettings
    ) -> AsyncGenerator[PlotHandle]:
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
                plot_handle = PlotHandle(self, plot_index)
                try:
                    yield plot_handle  # return the plot handle
                finally:  # this runs at the end of the context manager
                    self.submit_plot_command(  # remove the plot
                        lambda plot_tab: plot_tab.remove_plot(copy.copy(plot_index))
                    )
                return  # exit

    # ----------------------------------------------------------------------------------------------
    # private
    async def make_step_directory(
        self, data_directory: Path, step: SequenceStep, number: int
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

    async def prompt_handle_error(self, step: SequenceStep, error_message: str):
        """
        Ask the user how to handle a sequence step encountering an error.

        Raises
        ------
        CancelledError
            The sequence was cancelled.
        FatalSequenceError
            An invalid response was sent (this indicates an issue with the core codebase).
        """
        response = await self.send_prompt_and_wait(
            f"Sequence: Error in {step.name()}",
            f"{error_message}\n\nSkip current step or cancel the sequence?",
            {0: "Skip Current", 1: "Cancel"},
        )
        match response:
            case 0:  # skip current
                return
            case 1:  # cancel
                raise CancelledError
            case _:  # this should never run
                raise FatalSequenceError(f"Reponse was {response} when it should have been 0 or 1")

    async def send_prompt_and_wait(self, title: str, message: str, options: dict[int, str]) -> int:
        """Private helper function to send a message the the user and wait for a response."""
        receiver: DataLock[int | None] = DataLock(None)
        self.promptRequested.emit(title, message, options, receiver)  # request a prompt
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
    ):
        """
        Generate the default metadata and combine it with the **step**'s metadata, then write the
        data to a metadata file in the **step**'s data directory. Logs any errors.

        Raises
        ------
        CancelledError
            The sequence was cancelled.
        FatalSequenceError
            The sequence encountered a fatal error.
        """
        while True:
            try:
                file = directory.joinpath(METADATA_FILENAME)
                data = step.metadata()
                # we do it in this order so the step's metadata gets overridden if there are
                # duplicate keys. The default keys are reserved
                data.update(
                    {
                        "Start Datetime": str(start_datetime),
                        "End Datetime": str(datetime.now()),
                        "Cancelled": cancelled,
                        "Error": error_occurred,
                    }
                )
                with open(file, "w") as f:
                    # any non-JSON types are converted to strings
                    json.dump(data, f, indent=4, default=str)
                break  # exit the loop
            except Exception:
                logging.getLogger(__name__).exception("Failed to write metadata")

                response = await self.prompt_user(
                    step,
                    "Failed to record metadata.\n\nRetry or cancel sequence?",
                    {0: "Retry", 1: "Cancel"},
                )
                match response:
                    case 0:  # retry
                        continue
                    case 1:  # cancel
                        raise CancelledError
                    case _:  # this should never run
                        raise FatalSequenceError(
                            f"Reponse was {response} when it should have been 0 or 1"
                        )

    # used externally
    def submit_plot_command(self, command: Callable[[SequenceDisplayTab], None]):
        """
        Submit a **command** to the plot command queue. This is not for direct use by
        `SequenceStep`s.
        """
        self.plotCommandRequested.emit(command)
