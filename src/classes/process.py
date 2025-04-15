from ..instruments import InstrumentSet
from ..enums.status import SequenceStatus
from ..enums.status import StatusStateMachine
from ..utility.events import PROCESS_EVENTS
from ..utility.datetime import get_datetime
from .. import Files
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from typing import Any, Self, TYPE_CHECKING, Union
from .signals import CommandSignals, GraphSignals, InformationSignals
import time

if TYPE_CHECKING:
    from ..sequence_builder.tree_item import TreeItem


class Process(QObject):
    """
    Base class for all foreground processes. You must override:
    - `run()`
        - You must frequently call `wait()` to process events and handle pausing and canceling.
            - `wait()` returns a boolean indicating if the process has been canceled. If it has,
            you MUST end the process by cleaning up resources and returning.

    If you override `__init__()` make sure to call the base method.
    """

    def __init__(self, runner: "ProcessRunner", data: dict[str, Any]):
        """:param data: The data used to run this process."""
        super().__init__()
        self.data_as_dict = data
        self.process_runner = runner
        self.process_start_time = 0.0
        self.status = StatusStateMachine(SequenceStatus.INACTIVE)
        self.graph_signals = GraphSignals()
        self.info_signals = InformationSignals()

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
            if self.status.get() == SequenceStatus.CANCELED:
                return False
            # process events for 10 ms
            PROCESS_EVENTS()
        return True

    def data(self) -> dict[str, Any]:
        """Get this process' data."""
        return self.data_as_dict

    def init_start_time(self):
        """Call this right before `run()` to set the start time from `time.time()`."""
        self.process_start_time = time.time()

    def start_time(self) -> float:
        """Get the start time of this process."""
        return self.process_start_time

    def runner(self) -> "ProcessRunner":
        """Get the **ProcessRunner** running this process."""
        return self.process_runner

    def get_status(self) -> SequenceStatus:
        """Get the process status. This blocks until the mutex is available."""
        return self.status.get()

    def is_paused(self) -> bool:
        """Whether the process is paused. This blocks until the mutex is available."""
        return self.get_status().is_pause()

    def is_errored(self) -> bool:
        """Whether the process is in an error state. This blocks until the mutex is available."""
        return self.get_status().is_error()

    def cancel(self) -> Self:
        """Cancel the current process gracefully (do not emit signals)."""
        self.status.set(SequenceStatus.CANCELED)
        return self

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
        changed = self.status.set(status)
        if changed:
            self.info_signals.statusChanged.emit(status)
        return changed

    def communicate_error(self, message: str) -> Self:
        """Communicate to the process runner that an error occurred."""
        self.info_signals.errorOccurred.emit(message)
        return self

    def write_metadata(self, filename: str, start_time: float, end_time: float):
        """
        Create a metadata file and write the start and end time to it. You can override this method,
        but make sure to keep the same general format.

        :param filename: The full file name of the metadata file (including directories).
        :param start_time: The start time of the process, as returned by `time.time()`.
        :param end_time: The end time of the process, as returned by `time.time()`.
        """
        with open(filename, "w") as f:
            HEADERS = Files.Process.Headers.Metadata
            f.write(
                f"{HEADERS.START_TIME},{HEADERS.START_TIME_DATETIME},\
                    {HEADERS.END_TIME},{HEADERS.END_TIME_DATETIME}\n"
            )
            f.write(
                f"{start_time},{get_datetime(start_time)},{end_time},{get_datetime(end_time)}\n"
            )


class BackgroundProcess(QObject):
    """
    Base class for all background processes. You must override:
    - `run()`: Make sure to frequently call `time.sleep()`

    Additionally, you should frequently check `self.status` to see if you need to end the process.
    """

    errorOccurred = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, runner: "ProcessRunner", data: dict[str, Any] | None = None):
        """
        :param runner: The **ProcessRunner** running this process.
        """
        super().__init__()
        self.status = StatusStateMachine(SequenceStatus.INACTIVE)
        self.process_runner = runner

    def run(self):
        """(Virtual) Run the process."""
        pass

    def init_start_time(self):
        """Call this right before `run()` to set the start time from `time.time()`."""
        self.process_start_time = time.time()

    def start_time(self) -> float:
        """Get the start time of this process."""
        return self.process_start_time

    def runner(self) -> "ProcessRunner":
        """Get the **ProcessRunner** running this process."""
        return self.process_runner

    def update_status(self, status: SequenceStatus) -> bool:
        """
        Set the status. This blocks until the mutex is available.

        :returns: Whether the status changed.
        """
        # there are no signals to emit here
        return self.status.set(status)

    def cancel(self) -> Self:
        """Cancel the current process gracefully."""
        self.status.set(SequenceStatus.CANCELED)
        return self

    def communicate_error(self, message: str) -> Self:
        """Communicate to the process runner that an error occurred."""
        self.errorOccurred.emit(message)
        return self


class ProcessRunner(QObject):
    """Runs **Process**es. Contains parameters used by the `run()` method of a **Process**."""

    def __init__(self, parent: QObject, instruments: InstrumentSet, data_directory: str):
        """
        :param parent: The QObject that owns this runner. The parent should be in the same thread.
        :param instruments: The application's instruments.
        :param data_directory: The folder where all sequence data will be stored.
        """
        super().__init__(parent)
        self.application_instruments = instruments
        self.data_directory = data_directory
        self.process: Process | BackgroundProcess
        self.item: "TreeItem" | None = None

        self.command_signals = CommandSignals()
        self.graph_signals = GraphSignals()
        self.info_signals = InformationSignals()
        self.background_processes: list[BackgroundProcess] = []

    def pre_run(self) -> Self:
        """Runs before the current process."""
        self.process.update_status(SequenceStatus.ACTIVE)
        self.process.init_start_time()
        return self

    def run(self) -> Self:
        """Run the current process."""
        if isinstance(self.process, BackgroundProcess):
            self.pre_run()
            self.start_background_process(self.process)
        else:
            self.connect_process_signals()
            self.pre_run()
            self.process.run()
            self.post_run()
        return self

    def post_run(self):
        """This runs when the current process completes."""
        self.process.deleteLater()

    def connect_process_signals(self) -> Self:
        """Connect signals before the current process runs."""
        if not isinstance(self.process, BackgroundProcess):
            # up toward parent
            self.info_signals.connect_to_other(self.process.info_signals)
            # down toward children
            self.command_signals.pauseCommand.connect(self.process.pause)
            self.command_signals.unpauseCommand.connect(self.process.unpause)
            self.command_signals.cancelCommand.connect(self.process.cancel)
            self.command_signals.skipCommand.connect(self.process.skip)
        else:
            self.process.errorOccurred.connect(self.info_signals.errorOccurred)
        return self

    def set_current_proceses(self, process: Process | BackgroundProcess) -> Self:
        """Set the current process. This also updates the widget type."""
        self.process = process
        if not isinstance(process, BackgroundProcess):
            self.graph_signals.connect_to_other(process.graph_signals)
            self.info_signals.graphSignalsChanged.emit(process.graph_signals)
        return self

    def current_process(self) -> Process | BackgroundProcess:
        """Get the current process."""
        return self.process

    def set_current_item(self, item: "TreeItem") -> Self:
        """Set the current item and emit signals."""
        self.info_signals.currentItemChanged.emit(item, self.item)
        self.item = item
        return self

    def current_item(self) -> Union["TreeItem", None]:
        """Get the current item."""
        return self.item

    def instruments(self) -> InstrumentSet:
        """Get the instruments."""
        return self.application_instruments

    def directory(self) -> str:
        """Get the sequence data directory."""
        return self.data_directory

    # ----------------------------------------------------------------------------------------------
    # background process utilities
    def start_background_process(self, process: BackgroundProcess) -> Self:
        """Start a BackgroundProcess."""
        self.background_processes.append(process)

        thread = QThread()
        process.moveToThread(thread)
        thread.started.connect(process.run)
        process.finished.connect(thread.quit)
        thread.finished.connect(lambda: self.background_processes.remove(process))

        thread.start()
        return self

    def background_process_running(self) -> bool:
        """Whether any background processes are running."""
        return len(self.background_processes) > 0

    def cancel_background_processes(self) -> Self:
        """Cancel all background processes (usually at the end of a sequence)."""
        if self.background_process_running():
            for process in self.background_processes:
                process.cancel()
            while self.background_process_running():  # wait for them to actually finish
                PROCESS_EVENTS()

            self.background_processes.clear()
        return self
