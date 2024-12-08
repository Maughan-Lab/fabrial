from PyQt6.QtWidgets import QMainWindow, QSizePolicy
from PyQt6.QtCore import pyqtSignal


class SecondaryWindow(QMainWindow):
    """Secondary window with **closed** signal."""

    closed = pyqtSignal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def closeEvent(self, a0):  # overridden method
        if a0 is not None:
            self.closed.emit()
        super().closeEvent(a0)
