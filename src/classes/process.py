from ..enums.status import SequenceStatus
from ..enums.status import StatusStateMachine
from ..utility.events import PROCESS_EVENTS
from ..utility.datetime import get_datetime
from ..instruments import INSTRUMENTS
from ..classes.plotting import LineSettings
from .. import Files
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Any, Self, TYPE_CHECKING
from .signals import GraphSignals, InformationSignals
import time
import os
from typing import Callable
import polars as pl

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
        processes frequently call `wait()`, otherwise they will freeze the application.
        """
        pass

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
        """Get the start time of this process in seconds."""
        return self.process_start_time

    def runner(self) -> "ProcessRunner":
        """Get the **ProcessRunner** running this process."""
        return self.process_runner

    def status(self) -> SequenceStatus:
        """Get the process status."""
        return self.process_status.get()

    def is_canceled(self) -> bool:
        """Whether the process has been canceled."""
        return self.status() == SequenceStatus.CANCELED

    def cancel(self):
        """Cancel the current process gracefully (do not emit signals)."""
        self.process_status.set(SequenceStatus.CANCELED)

    def metadata(self, end_time: float) -> pl.DataFrame:
        """
        Create a DataFrame containing metadata for the process. By default, this DataFrame contains
        the start time, duration, and oven setpoint. You can override this method to add additional
        metadata.

        :param end_time: The end time of the process, as returned by `time.time()`.
        """
        HEADERS = Files.Process.Headers.Metadata
        start_time = self.start_time()
        duration = end_time - start_time
        setpoint = INSTRUMENTS.oven.get_setpoint()
        metadata = pl.DataFrame(
            {
                HEADERS.START_DATETIME: get_datetime(start_time),
                HEADERS.END_DATETIME: get_datetime(end_time),
                HEADERS.DURATION: duration,
                HEADERS.SETPOINT: setpoint,
            }
        )
        return metadata

    def write_metadata(self, metadata: pl.DataFrame):
        """Create a metadata file and write **metadata** to it."""
        metadata.write_csv(os.path.join(self.directory(), Files.Process.Filenames.METADATA))


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
        self.info_signals = InformationSignals(self)

    def wait(self, delay_ms: int, unpause_fn: Callable[[], bool] = lambda: False) -> bool:
        """
        Hold for **delay** milliseconds or as long as the process is paused, whichever is longer.
        This is where signals are processed, so be sure to call this frequently.

        :param delay_ms: How long to hold for.
        :param unpause_fn: A function that can cause the sequence to unpause if it is paused. This
        function takes no arguments and should return **True** to unpause, **False** otherwise.

        :returns: Whether the process should continue (i.e. it was not cancelled).
        """
        delay = delay_ms / 1000
        end_time = time.time() + delay
        while time.time() < end_time:
            if self.is_canceled():
                return False
            PROCESS_EVENTS()  # process events for 10 ms
        while self.is_paused():
            if self.is_canceled():
                return False
            PROCESS_EVENTS()  # process events for 10 ms
            if unpause_fn():
                self.unpause()

        return True

    def is_paused(self) -> bool:
        """Whether the process is paused."""
        return self.status().is_pause()

    def is_errored(self) -> bool:
        """Whether the process is in an error state."""
        return self.status().is_error()

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

    def error_pause(self) -> Self:
        """Pause the process with an error"""
        self.update_status(SequenceStatus.ERROR_PAUSED)
        return self

    def unpause(self) -> Self:
        """Unpause the process."""
        self.update_status(SequenceStatus.ACTIVE)
        return self

    def update_status(self, status: SequenceStatus) -> bool:
        """
        Set the status and emit signals.

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


class GraphingProcess(Process):
    """
    **Process** with graphing capabilities. This has the same override requirements as **Process**.
    """

    def __init__(self, runner: "ProcessRunner", data: dict[str, Any]):
        super().__init__(runner, data)
        self.graph_signals = GraphSignals(self)

    def init_line_plot(
        self,
        title: str,
        x_label: str,
        y_label: str,
        legend_label: str,
        line_color: str,
        line_width: float,
        symbol: str,
        symbol_color: str,
        symbol_size: int,
    ):
        """Initialize the sequence graph as a line plot."""
        settings = LineSettings(
            title,
            x_label,
            y_label,
            legend_label,
            line_color,
            line_width,
            symbol,
            symbol_color,
            symbol_size,
        )
        self.graph_signals.initPlot.emit(settings)

    def init_scatter_plot(
        self,
        title: str,
        x_label: str,
        y_label: str,
        legend_label: str,
        symbol: str = "o",
        symbol_color: str = "orange",
        symbol_size: int = 7,
    ):
        """Initialize the sequence graph as a scatter plot."""
        settings = LineSettings(
            title,
            x_label,
            y_label,
            legend_label,
            None,
            None,
            symbol,
            symbol_color,
            symbol_size,
        )
        self.graph_signals.initPlot.emit(settings)


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

    def wait(self, delay_ms: int, unpause_fn: Callable[[], bool] = lambda: False) -> bool:
        """
        Hold for **delay** milliseconds. This is where signals are processed, so be sure to call
        this frequently.

        :returns: Whether the process should continue (i.e. it was not cancelled).
        """
        delay = delay_ms / 1000
        end_time = time.time() + delay
        # wait_interval = delay_ms / 100  # this is arbitrary and seemed like a good value
        while time.time() < end_time:
            if self.is_canceled():
                return False
            # process events for 10 ms
            PROCESS_EVENTS()
        return True

    def update_status(self, status: SequenceStatus) -> bool:
        """
        Set the status.

        :returns: Whether the status changed.
        """
        # there are no signals to emit here
        return self.process_status.set(status)

    def communicate_error(self, message: str) -> Self:
        """Communicate to the process runner that an error occurred."""
        self.errorOccurred.emit(message)
        return self
