from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QMainWindow, QSizePolicy, QWidget


class SecondaryWindow(QMainWindow):
    """
    Secondary window with `closed` signal.

    Parameters
    ----------
    title
        The window title text.
    central_widget
        The widget to set as the central widget (optional).
    parent
        This window's parent (optional).

    Notes
    -----
    If **parent** is specified, the created window will always be displayed on top of the parent.
    You must call `show()` on the window as normal.
    """

    closed = pyqtSignal()

    def __init__(
        self, title: str, central_widget: QWidget | None = None, parent: QWidget | None = None
    ):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle(title)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCentralWidget(central_widget)  # takes ownership
        if central_widget is not None:
            central_widget.setVisible(True)

    def closeEvent(self, event: QCloseEvent | None):  # overridden method
        if event is not None:
            self.closed.emit()
        QMainWindow.closeEvent(self, event)

    def close_silent(self):
        """Close the window without emitting the `closed` signal."""
        self.blockSignals(True)
        self.close()
        self.blockSignals(False)
