from typing import Any
from ....classes.process import ProcessInputs
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal


class ProcessSignals(QObject):
    """Signals that the process can emit."""

    errorOccurred = pyqtSignal(str)


class BaseProcess:
    """
    Base class for all linked processes. You must override:
    - `run()`

    If you override `__init__()` make sure to call the base method.
    """

    def __init__(
        self,
        data: dict[str, Any],
        signals: ProcessSignals = ProcessSignals(),
        visual_widget: QWidget | None = None,
    ):
        """
        :param data: The data used to run this process.
        :param signals: A ProcessSignals object for sending signals.
        :param visual_widget: The widget associated with this process (i.e. for graphing).
        """
        self.data = data
        self.signals = signals
        self.linked_widget = visual_widget

        self.paused = False
        self.cancelled = False

    def run(self, inputs: ProcessInputs):
        """
        Run the process. When subclassing this method, you must ensure that long-running processes
        frequently call `time.sleep()`, otherwise they will freeze the application.

        :param inputs: A container with multiple useful inputs, such as application-wide instruments
        and the process runner's QThreadPool, which background processes can add themselves to.
        """
        pass

    def cancel(self):
        """Cancel the current process gracefully."""
        self.cancelled = True

    def set_paused(self, paused: bool):
        """Set whether the current process is paused."""
        self.paused = paused

    def pause(self):
        """Pause the current process."""
        self.set_paused(True)

    def unpause(self):
        """Unpause the current process."""
        self.set_paused(False)

    def is_paused(self) -> bool:
        """Whether the current process is paused."""
        return self.paused

    def visual_widget(self) -> QWidget | None:
        """
        Get a reference to this process' linked visual widget (for displaying graphs, etc.).
        """
        return self.linked_widget

    def communicate_error(self, message: str):
        """Communicate to the process runner that an error occurred."""
        self.signals.errorOccurred.emit(message)
