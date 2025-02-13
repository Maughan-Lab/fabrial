from PyQt6.QtCore import QRunnable, pyqtSlot
from custom_widgets.plot import PlotWidget
from classes.points import TemperaturePoint


class GraphingThread(QRunnable):
    """Thread for plotting points."""

    # TODO: verify that this is even useful

    def __init__(self, plot: PlotWidget, point: TemperaturePoint, point_color: str):
        super().__init__()
        self.plot = plot
        self.point = point
        self.point_color = point_color

    @pyqtSlot()
    def run(self):
        self.plot.scatter(
            self.point.time, self.point.temperature, color=self.point_color, marker="."
        )
        self.plot.tight_layout()
        self.plot.draw()
