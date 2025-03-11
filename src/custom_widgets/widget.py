from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import pyqtSignal


class Widget(QWidget):
    """QWidget with a **closed** signal."""

    closed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

    def closeEvent(self, event):  # overridden method
        if event is not None:
            self.closed.emit()
        super().closeEvent(event)
