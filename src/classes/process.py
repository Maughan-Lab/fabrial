from ..enums.status import SequenceStatus
from ..enums.status import StatusStateMachine
from ..utility.events import PROCESS_EVENTS
from ..utility.datetime import get_datetime
from .. import Files
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Any, Self, TYPE_CHECKING
from .signals import GraphSignals, InformationSignals
import time
import os

if TYPE_CHECKING:
    from .process_runner import ProcessRunner


class BaseProcess(QObject):
    """Base class for all processes."""

    DIRECTORY = ""

    def __init__(self, runner: "ProcessRunner", data: dict[str, Any]):
        """:param data: The data used tro run this process."""
        super().__init__()
        self.data_as_dict = data
        self.process_runner = runner
        self.process_start_time = 0.0
        self.process_status = StatusStateMachine(SequenceStatus.INACTIVE)
        self.data_directory = ""

    def run(self):
        """
        (Virtual) Run the process. When subclassing this method, you must ensure that long-running
        processes frequently call `time.sleep()`, otherwise they will freeze the application.
        """
        pass

    def wait(self, delay_ms: int) -> bool:
        """
        Hold for **delay** milliseconds or as long as the process is paused, whichever is longer.
        This is where signals are processed, so be sure to call this frequently.

        :returns: Whether the process should continue (i.e. it was not cancelled).
        """
        delay = delay_ms / 1000
        end_time = time.time() + delay
        # wait_interval = delay_ms / 100  # this is arbitrary and seemed like a good value
        while time.time() < end_time or self.is_paused():
            if self.status() == SequenceStatus.CANCELED:
                return False
            # process events for 10 ms
            PROCESS_EVENTS()
        return True

    def data(self) -> dict[str, Any]:
        """Get this process' data."""
        return self.data_as_dict

    def set_directory(self, data_directory: str):
        """Set the data directory."""
        self.data_directory = data_directory

    def directory(self) -> str:
        """
        Get the directory to write this process' data to. The name and creation of this directory is
        managed by the **ProcessRunner**, so you can assume it already exists.
        """
        return self.data_directory

    def init_start_time(self):
        """Call this right before `run()` to set the start time from `time.time()`."""
        self.process_start_time = time.time()

    def start_time(self) -> float:
        """Get the start time of this process."""
        return self.process_start_time

    def runner(self) -> "ProcessRunner":
        """Get the **ProcessRunner** running this process."""
        return self.process_runner

    def status(self) -> SequenceStatus:
        """Get the process status. This blocks until the mutex is available."""
        return self.process_status.get()

    def is_paused(self) -> bool:
        """Whether the process is paused. This blocks until the mutex is available."""
        return self.status().is_pause()

    def is_errored(self) -> bool:
        """Whether the process is in an error state. This blocks until the mutex is available."""
        return self.status().is_error()

    def cancel(self):
        """Cancel the current process gracefully (do not emit signals)."""
        self.process_status.set(SequenceStatus.CANCELED)

    def write_metadata(self, directory: str, start_time: float, end_time: float):
        """
        Create a metadata file and write the start and end time to it. You can override this method,
        but make sure to keep the same general format.

        :param directory: The full path to the process' data directory.
        :param start_time: The start time of the process, as returned by `time.time()`.
        :param end_time: The end time of the process, as returned by `time.time()`. If not
        specified, the current time is used.
        """
        with open(os.path.join(directory, Files.Process.Filenames.METADATA), "w") as f:
            HEADERS = Files.Process.Headers.Metadata
            f.write(f"{HEADERS.START_DATETIME},{HEADERS.END_DATETIME},{HEADERS.DURATION}\n")
            duration = end_time - start_time
            f.write(f"{get_datetime(start_time)},{get_datetime(end_time)},{duration}\n")


class Process(BaseProcess):
    """
    Base class for all foreground processes. You must override:
    - `DIRECTORY`
        - The name of the process' data directory.
        - Optional if the process does not record data.
    - `run()`
        - You must frequently call `wait()` to process events and handle pausing and canceling.
            - `wait()` returns a boolean indicating if the process has been canceled. If it has,
            you MUST end the process by cleaning up resources and returning.

    If you override `__init__()` make sure to call the base method.
    """

    def __init__(self, runner: "ProcessRunner", data: dict[str, Any]):
        """:param data: The data used to run this process."""
        super().__init__(runner, data)
        self.graph_signals = GraphSignals()
        self.info_signals = InformationSignals()

    def skip(self) -> Self:
        """
        Skip the current process. By default, this just calls **cancel()**. You can override this
        for nested processes to skip an inner process instead.
        """
        self.cancel()
        return self

    def pause(self) -> Self:
        """Pause the process."""
        self.update_status(SequenceStatus.PAUSED)
        return self

    def unpause(self) -> Self:
        """Unpause the process."""
        self.update_status(SequenceStatus.ACTIVE)
        return self

    def update_status(self, status: SequenceStatus) -> bool:
        """
        Set the status and emit signals. This blocks until the mutex is available.

        :returns: Whether the status was updated (a valid state change occurred).
        """
        changed = self.process_status.set(status)
        if changed:
            self.info_signals.statusChanged.emit(status)
        return changed

    def communicate_error(self, message: str) -> Self:
        """Communicate to the process runner that an error occurred."""
        self.info_signals.errorOccurred.emit(message)
        return self


class BackgroundProcess(BaseProcess):
    """
    Base class for all background processes. You must override:
    - DIRECTORY
        - The directory to create for storing the process' data.
        - Optional if there is no data to record.
    - `run()`
        - Make sure to frequently call `wait()`
    """

    errorOccurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, runner: "ProcessRunner", data: dict[str, Any]):
        """
        :param runner: The **ProcessRunner** running this process.
        """
        super().__init__(runner, data)

    def update_status(self, status: SequenceStatus) -> bool:
        """
        Set the status. This blocks until the mutex is available.

        :returns: Whether the status changed.
        """
        # there are no signals to emit here
        return self.process_status.set(status)

    def communicate_error(self, message: str) -> Self:
        """Communicate to the process runner that an error occurred."""
        self.errorOccurred.emit(message)
        return self
