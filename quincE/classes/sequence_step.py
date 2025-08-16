from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from abc import abstractmethod
from asyncio import CancelledError
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Protocol

from ..classes import FatalSequenceError, PlotHandle, PlotSettings
from ..constants.paths.sequence import METADATA_FILENAME


class StepRunner:
    """Runs `SequenceStep`s and provides utilities ."""

    def __init__(self):
        pass

    async def run_steps(self, steps: Iterable[SequenceStep], data_directory: Path):
        """Run the provided **steps** sequentially."""
        for i, step in enumerate(steps):
            # create the data directory first
            step_data_directory = await self.make_step_directory(data_directory, i, step)
            # TODO: figure out a way to make the step bold in the model
            # run the step
            await self.run_single_step(step, step_data_directory)

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
            error_occurred = True
            logging.getLogger(__name__).exception("Sequence step error")
            if not (
                await self.prompt_handle_error("The current step encountered an error.")
                and await self.record_metadata(
                    step_data_directory, step, start_datetime, cancelled, error_occurred
                )
            ):
                raise CancelledError

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
                f"Failed to create data directory {step_data_directory}"
            ):
                raise CancelledError
        return step_data_directory

    async def prompt_handle_error(self, error_message: str) -> bool:
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
        response = await self.prompt_user(
            f"{error_message}\nSkip current step or cancel the sequence?",
            {0: "Skip Current", 1: "Cancel"},
        )
        match response:
            case 0:  # skip current
                return True
            case 1:  # cancel
                return False
            case _:  # this should never run
                raise FatalSequenceError(f"Reponse was {response} when it should have been 0 or 1")

    async def prompt_user(self, message: str, options: dict[int, str]) -> int:
        """
        Show a popup prompt to the user and wait for a response.

        Parameters
        ----------
        message
            The prompt's text.
        options
            A mapping of values to options in the prompt. For example,
            `{1: "First Option", 2: "Second Option}` will show a prompt with options "First Option"
            and "Second Option". If the user selects "First Option", this function will return `1`.
            If the user selects "Second Option", this function will return `2`.
        """
        # TODO
        return 0

    # TODO: should this function kill the sequence step? You could rename it `exit_with_error()` in
    # that case
    def notify_error(self, error_message: str):
        """
        Notify the user that can error has occurred. In general, the sequence step should exit after
        calling this function.
        """
        # TODO
        pass

    def exit_with_error(self, error_message: str):
        """Kill the entire sequence and notify the user that a fatal error occurred."""
        pass

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
            return await self.prompt_handle_error("Failed to record metadata for the current step.")
        return True

    def create_plot(
        self, step: SequenceStep, tab_text: str, plot_settings: PlotSettings
    ) -> PlotHandle:
        """
        Create a new plot on the visuals tab and return a handle to it.

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
        # TODO
        pass

    # TODO: cancellation
    # TODO: status


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
        Reset this step to its original state (i.e. before `run()` was called). This sequence step
        might be re-used, so it must be resettable. An easy implementation is to call `__init__()`
        to reinitialize with the original parameters.
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
        """Sleep until **when**, which is a number as returned by `time.time()`."""
        await self.sleep(0)
        while time.time() < when:
            await self.sleep(0)
