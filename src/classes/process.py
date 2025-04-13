from ..instruments import InstrumentSet
from ..enums.status import SequenceStatus
from ..classes.mutex import StatusStateMachine
from ..classes.null import Null
from ..utility.events import PROCESS_SIGNALS
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget
from typing import Any, Self, Callable, TYPE_CHECKING, Union
import time

if TYPE_CHECKING:
    from ..sequence_builder.tree_item import TreeItem


class Process(QObject):
    """
    Base class for all foreground processes. You must override:
    - `SIGNALS_TYPE`
    - `WIDGET_TYPE` - the type of widget used to display this process' data. Do not override if
    there is no data.

    - `run()`

    If you override `__init__()` make sure to call the base method.

    You must also ensure the process regularly checks its status to see if it should pause or
    cancel.
    """

    errorOccurred = pyqtSignal(str)
    statusChanged = pyqtSignal(SequenceStatus)
    # you can emit this for nested processes that have widgets
    widgetTypeChanged = pyqtSignal(object)  # this is a Callable[[], QWidget] | Null
    # you can emit this for nested processes that change the item
    currentItemChanged = pyqtSignal(object, object)  # new, previous (TreeItem | Null)

    WIDGET_TYPE: Callable[[], QWidget] | Null = Null()

    def __init__(self, runner: "ProcessRunner", data: dict[str, Any] | None = None):
        """:param data: The data used to run this process."""
        super().__init__()
        self.data = data
        self.runner = runner
        self.status = StatusStateMachine(SequenceStatus.INACTIVE)

    def run(self):
        """
        (Virtual) Run the process. When subclassing this method, you must ensure that long-running
        processes frequently call `time.sleep()`, otherwise they will freeze the application.
        """
        pass

    def wait(self, delay: float) -> bool:
        """
        Hold for **delay** seconds or as long as the process is paused, whichever is longer. This is
        where signals are processed, so be sure to call this frequently.

        :returns: Whether the process should continue (i.e. it was not cancelled).
        """
        end_time = time.time() + delay
        wait_interval = delay / 100  # this is arbitrary and seemed like a good value
        while time.time() < end_time or self.is_paused():
            PROCESS_SIGNALS()
            if self.status.get() == SequenceStatus.CANCELED:
                return False
            time.sleep(wait_interval)
        return True

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
            self.statusChanged.emit(status)
        return changed

    def communicate_error(self, message: str) -> Self:
        """Communicate to the process runner that an error occurred."""
        self.errorOccurred.emit(message)
        return self


# TODO: make this a QObject instead and update the process runner methods
class BackgroundProcess(QThread):
    """
    Base class for all background processes. You must override:
    - `run()`: Make sure to frequently call `time.sleep()`

    Additionally, you should frequently check `self.status` to see if you need to end the process.
    """

    errorOccurred = pyqtSignal(str)

    def __init__(self, runner: "ProcessRunner", data: dict[str, Any] | None = None):
        """
        :param runner: The **ProcessRunner** running this process.
        """
        super().__init__()
        self.status = StatusStateMachine(SequenceStatus.INACTIVE)
        self.runner = runner

    def run(self):
        """(Virtual) Run the process."""
        pass

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

    errorOccurred = pyqtSignal(str)
    statusChanged = pyqtSignal(SequenceStatus)
    widgetTypeChanged = pyqtSignal(object)  # this is a Callable[[], QWidget] | Null
    currentItemChanged = pyqtSignal(object, object)  # new, previous (TreeItem | Null)

    pauseCommand = pyqtSignal()
    unpauseCommand = pyqtSignal()
    cancelCommand = pyqtSignal()
    skipCommand = pyqtSignal()

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
        self.item: "TreeItem" | Null = Null()

        self.background_processes: list[BackgroundProcess] = []

    def pre_run(self) -> Self:
        """Runs before the current process."""
        self.process.update_status(SequenceStatus.ACTIVE)
        # PROCESS_SIGNALS()
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
        self.process.errorOccurred.connect(self.errorOccurred.emit)

        if not isinstance(self.process, BackgroundProcess):
            # up toward parent
            self.process.statusChanged.connect(self.statusChanged)
            self.process.errorOccurred.connect(self.errorOccurred)
            self.process.widgetTypeChanged.connect(self.widgetTypeChanged)
            self.process.currentItemChanged.connect(self.currentItemChanged)
            # down toward children
            self.pauseCommand.connect(self.process.pause)
            self.unpauseCommand.connect(self.process.unpause)
            self.cancelCommand.connect(self.process.cancel)
            self.skipCommand.connect(self.process.skip)

        return self

    def set_current_proceses(self, process: Process | BackgroundProcess) -> Self:
        """Set the current process. This also updates the widget type."""
        self.process = process
        if not isinstance(process, BackgroundProcess):
            self.widgetTypeChanged.emit(process.WIDGET_TYPE)
        return self

    def current_process(self) -> Process | BackgroundProcess:
        """Get the current process."""
        return self.process

    def set_current_item(self, item: "TreeItem") -> Self:
        """Set the current item and emit signals."""
        self.currentItemChanged.emit(item, self.item)
        self.item = item
        return self

    def current_item(self) -> Union["TreeItem", Null]:
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
    def start_background_process(self, process: "BackgroundProcess") -> Self:
        """Start a BackgroundProcess."""
        self.background_processes.append(process)
        process.finished.connect(process.deleteLater)
        process.start()
        return self

    def background_process_running(self) -> bool:
        """Whether any background processes are running."""
        return len(self.background_processes) > 0

    def cancel_background_processes(self) -> Self:
        """Cancel all background processes (usually at the end of a sequence)."""
        if self.background_process_running():
            for process in self.background_processes:
                process.cancel()
                process.wait()  # wait for them to actually finish
            self.background_processes.clear()
        return self
