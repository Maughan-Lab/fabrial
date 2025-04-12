from ..instruments import InstrumentSet
from ..enums.status import SequenceStatus
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget
import time
from typing import TYPE_CHECKING, Any, Self, Union, Callable

if TYPE_CHECKING:
    from ..sequence_builder.tree_item import TreeItem


class ProcessRunner(QObject):
    """Runs **Process**es. Contains parameters used by the `run()` method of a **Process**."""

    errorOccurred = pyqtSignal(str)
    statusChanged = pyqtSignal(SequenceStatus)

    def __init__(self, instruments: InstrumentSet, data_directory: str):
        """
        :param instruments: The application's instruments.
        :param data_directory: The folder where all sequence data will be stored.
        """
        super().__init__()

        self.application_instruments = instruments
        self.data_directory = data_directory
        self.process: "Process"
        self.item: "TreeItem"

        self.background_processes: list["BackgroundProcess"] = []

    def run(self):
        """Run the current process."""
        self.process.errorOccurred.connect(self.errorOccurred.emit)
        self.process.statusChanged.connect(self.statusChanged.emit)

        self.item.set_running(True)
        self.process.update_status(SequenceStatus.ACTIVE)
        self.process.run()
        self.item.set_running(False)

    def set_current_proceses(self, process: "Process") -> Self:
        """Set the current process."""
        self.process = process
        return self

    def current_process(self) -> "Process":
        """Get the current process."""
        return self.process

    def set_process_widget(self, widget: QWidget) -> Self:
        """Set the current process' visual widget."""
        self.process.set_visual_widget(widget)
        return self

    def set_current_item(self, item: "TreeItem") -> Self:
        """Set the current item."""
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

    def update_status(self, status) -> Self:
        """Update the current process' status and send signals."""
        self.process.set_status(status)
        self.statusChanged.emit(status)
        return self

    def pause(self) -> Self:
        """Pause the current process."""
        self.update_status(SequenceStatus.PAUSED)
        return self

    def unpause(self) -> Self:
        """Unpause the current process."""
        self.update_status(SequenceStatus.ACTIVE)
        return self

    def cancel(self) -> Self:
        """Cancel the current process (do not emit signals)."""
        self.process.set_status(SequenceStatus.CANCELED)
        return self

    # ----------------------------------------------------------------------------------------------
    # background process utilities
    def start_background_process(self, process: "BackgroundProcess") -> Self:
        """Start a BackgroundProcess."""
        self.background_processes.append(process)
        process.finished.connect(lambda: self.background_processes.remove(process))
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
            while self.background_process_running():  # wait for them to actually finish
                time.sleep(0.1)
            self.background_processes.clear()
        return self


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

    WIDGET_TYPE: Callable[[], QWidget] | None = None

    def __init__(self, runner: ProcessRunner, data: dict[str, Any] | None = None):
        """:param data: The data used to run this process."""
        super().__init__()

        self.data = data
        self.widget: QWidget | None = None
        self.runner = runner

        self.status = SequenceStatus.INACTIVE

    def run(self):
        """
        Run the process. When subclassing this method, you must ensure that long-running processes
        frequently call `time.sleep()`, otherwise they will freeze the application.

        :param runner: The **ProcessRunner** running this process.
        """
        pass

    def set_status(self, status: SequenceStatus):
        """Set the process status (does not emit signals)."""
        self.status = status

    def update_status(self, status: SequenceStatus):
        """Set the status and emit signals."""
        self.set_status(status)
        self.statusChanged.emit(status)

    def get_status(self) -> SequenceStatus:
        """Get the process status."""
        return self.status

    def cancel(self) -> Self:
        """Cancel the current process gracefully (do not emit signals)."""
        self.set_status(SequenceStatus.CANCELED)
        return self

    def pause(self) -> Self:
        """Pause the process without an error state."""
        self.update_status(SequenceStatus.PAUSED)
        return self

    def pause_error(self) -> Self:
        """Pause the process in an error state."""
        self.update_status(SequenceStatus.ERROR_PAUSED)
        return self

    def unpause(self) -> Self:
        """Unpause the process."""
        self.update_status(SequenceStatus.ACTIVE)
        return self

    def is_paused(self) -> bool:
        """Whether the current process is paused."""
        return self.status.is_pause()

    def set_visual_widget(self, widget: QWidget):
        """Set this process' visual widget."""
        self.widget = widget

    def visual_widget(self) -> QWidget | None:
        """
        Get a reference to this process' linked visual widget (for displaying graphs, etc.).
        """
        return self.widget

    def communicate_error(self, message: str) -> Self:
        """Communicate to the process runner that an error occurred."""
        self.errorOccurred.emit(message)
        return self


class BackgroundProcess(QThread):
    """
    Base class for all background processes. You must override:
    - `run()`: Make sure to frequently call `time.sleep()`

    Additionally, you should frequently check `self.status` to see if you need to end the process.
    """

    errorOccurred = pyqtSignal(str)
    statusChanged = pyqtSignal(SequenceStatus)

    def __init__(self, runner: ProcessRunner, data: dict[str, Any] | None = None):
        """
        :param runner: The **ProcessRunner** running this process.
        """
        super().__init__()
        self.status = SequenceStatus.INACTIVE

    def cancel(self) -> Self:
        """Cancel the current process gracefully."""
        self.status = SequenceStatus.CANCELED
        return self

    def communicate_error(self, message: str) -> Self:
        """Communicate to the process runner that an error occurred."""
        self.errorOccurred.emit(message)
        return self
