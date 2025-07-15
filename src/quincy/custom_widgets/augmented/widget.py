from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLayout, QSizePolicy, QWidget


class SignalWidget(QWidget):
    """QWidget with a **closed** signal."""

    closed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None):
        QWidget.__init__(self, parent)

    def closeEvent(self, event):  # overridden method
        if event is not None:
            self.closed.emit()
        QWidget.closeEvent(self, event)


class FixedWidget(QWidget):
    """QWidget with a fixed size."""

    def __init__(self, parent: QWidget | None = None):
        QWidget.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)


class Widget(QWidget):
    """QWidget that automatically sets the layout."""

    def __init__(self, layout: QLayout | None = None):
        """:param layout: The layout to initialize with."""
        QWidget.__init__(self)
        if layout is not None:
            self.setLayout(layout)
