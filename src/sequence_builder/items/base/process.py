from typing import Any, TYPE_CHECKING
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtSignal

if TYPE_CHECKING:
    from ....classes.process import ProcessInputs


class ProcessSignals(QObject):
    """Signals that the process can emit."""

    errorOccurred = pyqtSignal(str)


class BaseProcess:
    """
    Base class for all linked processes. You must override:
    - `SIGNALS_TYPE`

    - `run()`
    - `visual_widget()`

    If you override `__init__()` make sure to call the base method.

    You must also ensure the process regularly checks the `self.paused` and `self.canceled` flags.
    The process should pause if `self.paused` is `True` and cancel itself if `self.canceled` is
    `True`.
    """

    SIGNALS_TYPE = ProcessSignals

    def __init__(self, data: dict[str, Any]):
        """:param data: The data used to run this process."""
        self.data = data
        self.signals = self.SIGNALS_TYPE()

        self.paused = False
        self.cancelled = False

    def run(self, inputs: "ProcessInputs"):
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

    def is_paused(self) -> bool:
        """Whether the current process is paused."""
        return self.paused

    def visual_widget(self) -> QWidget | None:
        """
        Get a reference to this process' linked visual widget (for displaying graphs, etc.).
        """
        return None

    def communicate_error(self, message: str):
        """Communicate to the process runner that an error occurred."""
        self.signals.errorOccurred.emit(message)
