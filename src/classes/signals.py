from PyQt6.QtCore import QObject, pyqtSignal
from typing import Self
from ..enums.status import SequenceStatus
from ..classes.plotting import LineSettings


class GraphSignals(QObject):
    """
    Container for graph signals with convenient connection methods. These signals go from child to
    parent.
    """

    initPlot = pyqtSignal(LineSettings)
    clear = pyqtSignal()
    addPoint = pyqtSignal(float, float)  # x, y

    def connect_to_other(self, other: Self) -> Self:
        """All of **other**'s signals will fire this object's corresponding signal."""
        other.initPlot.connect(self.initPlot)
        other.clear.connect(self.clear)
        other.addPoint.connect(self.addPoint)

        return self


class CommandSignals(QObject):
    """
    Container for command signals (i.e. pausing and canceling). These signals go from parent to
    child.
    """

    pauseCommand = pyqtSignal()
    unpauseCommand = pyqtSignal()
    cancelCommand = pyqtSignal()
    skipCommand = pyqtSignal()

    def connect_to_other(self, other: Self) -> Self:
        """All of this object's signals will fire **other**'s corresponding signal."""
        self.pauseCommand.connect(other.pauseCommand)
        self.unpauseCommand.connect(other.unpauseCommand)
        self.cancelCommand.connect(other.cancelCommand)
        self.skipCommand.connect(other.skipCommand)

        return self


class InformationSignals(QObject):
    """Container for information signals. These signals go from child to parent."""

    errorOccurred = pyqtSignal(str)  # contains a message to show
    statusChanged = pyqtSignal(SequenceStatus)
    currentItemChanged = pyqtSignal(object, object)  # new, previous (TreeItem | None)

    def connect_to_other(self, other: Self) -> Self:
        """All of **other**'s signals fire this object's signals."""
        other.errorOccurred.connect(self.errorOccurred)
        other.statusChanged.connect(self.statusChanged)
        other.currentItemChanged.connect(self.currentItemChanged)

        return self
