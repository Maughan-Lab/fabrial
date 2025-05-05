from typing import Self

from PyQt6.QtCore import QObject, pyqtSignal

from ..classes.plotting import LineSettings


class GraphSignals(QObject):
    """
    Container for graph signals with convenient connection methods. These signals go from child to
    parent.
    """

    # TODO: this needs to also have an identifier string for the name of the tab
    initPlot = pyqtSignal(int, LineSettings)
    """
    Initialize a plot. Emit with the plot index as an **int** and a **LineSettings** object for the
    line settings. If creating multiple plots, you must call this with sequential plot indexes
    (i.e. 0, 1, 2 and not 0, 2, 1).
    """
    reset = pyqtSignal()
    """
    Destroy all plots. Emit with no parameters. After this is emitted, other signals should not be
    emitted until a new plot is initialized.
    """
    clear = pyqtSignal(int)
    """
    Clear a plot. Emit with the index of the plot to clear as an **int**.
    """
    addPoint = pyqtSignal(int, float, float)  # x, y
    """
    Add a point to a plot. Emit with the plot index as an **int** and `x`, `y`, where `x` and `y`
    are **float**s.
    """
    saveFig = pyqtSignal(int, str)
    """Save a figure. Emit with the plot index as an **int** and the filename as a **str**."""
    setLogScale = pyqtSignal(int, object, object)
    """
    Set whether a plot uses a logarithmic scale. Emit with the plot index as an **int** and
    `x_is_log` and `y_is_log`, where both are either **bool** or **None**. Sending a **None** will
    leave the log scale state unchanged.
    """

    def connect_to_other(self, other: Self):
        """All of **other**'s signals will fire this object's corresponding signal."""
        other.initPlot.connect(self.initPlot)
        other.reset.connect(self.reset)
        other.clear.connect(self.clear)
        other.addPoint.connect(self.addPoint)
        other.saveFig.connect(self.saveFig)
        other.setLogScale.connect(self.setLogScale)


class CommandSignals(QObject):
    """
    Container for command signals (i.e. pausing and canceling). These signals go from parent to
    child.
    """

    pauseCommand = pyqtSignal()
    unpauseCommand = pyqtSignal()
    cancelCommand = pyqtSignal()
    skipCommand = pyqtSignal()

    def connect_to_other(self, other: Self):
        """All of this object's signals will fire **other**'s corresponding signal."""
        self.pauseCommand.connect(other.pauseCommand)
        self.unpauseCommand.connect(other.unpauseCommand)
        self.cancelCommand.connect(other.cancelCommand)
        self.skipCommand.connect(other.skipCommand)
