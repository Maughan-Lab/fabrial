import asyncio
import logging
import time
from asyncio import CancelledError, TaskGroup
from collections.abc import Iterable
from pathlib import Path
from queue import Empty, Queue

from PyQt6.QtCore import QThread, pyqtSignal

from ..enums import SequenceCommand, SequenceStatus
from .exceptions import FatalSequenceError
from .lock import DataLock
from .sequence_step import SequenceStep
from .step_runner import StepRunner


class SequenceThread(QThread):
    """A `QThread` where the sequence runs."""

    statusChanged = pyqtSignal(SequenceStatus)
    """
    Emitted when the sequence's status changes.

    Sends
    - The status as a `SequenceStatus`.
    """
    promptRequested = pyqtSignal(str, str, dict, DataLock)  # see `StepRunner`
    plotCommandRequested = pyqtSignal(object)  # see `StepRunner`
    stepStateChanged = pyqtSignal("qint64", bool)  # see `StepRunner`

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
        # create the runner
        self.runner = StepRunner()
        self.runner.moveToThread(self)
        self.runner.promptRequested.connect(self.promptRequested)
        self.runner.plotCommandRequested.connect(self.plotCommandRequested)
        self.runner.stepStateChanged.connect(self.stepStateChanged)

    def run(self):  # overridden
        try:
            self.statusChanged.emit(SequenceStatus.Active)
            cancelled = not asyncio.run(self.run_actual())
            self.statusChanged.emit(
                SequenceStatus.Cancelled if cancelled else SequenceStatus.Completed
            )
        except* (FatalSequenceError, Exception):
            logging.getLogger(__name__).exception("Sequence raised a fatal exception")
            self.statusChanged.emit(SequenceStatus.FatalError)

    async def run_actual(self) -> bool:
        """
        The actual run function (required so we can do `asyncio.run()`). Returns whether the
        sequence ended normally. This can raise exceptions.
        """
        async with TaskGroup() as task_group:
            sequence_task = task_group.create_task(
                self.runner.run_steps(self.steps, self.data_directory)
            )
            monitor_task = task_group.create_task(self.monitor())
            # if either task ends, cancel the other
            monitor_task.add_done_callback(lambda _: sequence_task.cancel())
            sequence_task.add_done_callback(lambda _: monitor_task.cancel())

        return not sequence_task.cancelled()

    async def monitor(self) -> None:
        """Monitor for messages and commands."""
        while True:
            self.check_commands()
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
                    case SequenceCommand.RaiseFatal:
                        raise FatalSequenceError("The main thread requested a fatal error")
        except Empty:
            pass

    def pause(self):
        """Pause the sequence."""
        self.statusChanged.emit(SequenceStatus.Paused)
        while True:
            try:
                command = self.command_queue.get_nowait()
                match command:
                    case SequenceCommand.Cancel:
                        raise CancelledError
                    case SequenceCommand.Unpause:
                        self.statusChanged.emit(SequenceStatus.Active)
                        return
                    case SequenceCommand.Pause:  # ignore additional pauses
                        pass
            except Empty:
                pass
            time.sleep(0)  # this is not `asyncio.sleep()`
