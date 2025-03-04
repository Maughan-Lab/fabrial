from PyQt6.QtWidgets import QMainWindow, QWidget, QSizePolicy
from PyQt6.QtCore import pyqtSignal


class SecondaryWindow(QMainWindow):
    """Secondary window with **closed** signal."""

    closed = pyqtSignal()

    def __init__(
        self, title: str, central_widget: QWidget | None = None, parent: QWidget | None = None
    ):
        """
        Create a secondary window. If **parent** is specified, the created window will always be
        displayed on top of the parent.

        :param title: The window title text.
        :param central_widget: The widget to set as the central widget (optional).
        :param parent: This window's parent (optional).
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCentralWidget(central_widget)
        self.show()

    def closeEvent(self, a0):  # overridden method
        if a0 is not None:
            self.closed.emit()
        super().closeEvent(a0)
