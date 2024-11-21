from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt6.QtGui import QResizeEvent
from helper_functions.layouts import add_to_layout  # ../helper_functions
import matplotlib
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT as Toolbar,
)
from matplotlib.figure import Figure

matplotlib.use("qtagg")


class PlotWidget(QWidget):
    """Plot class for displaying **matplotlib** plots."""

    def __init__(self, figsize: tuple[int, int], dpi: int):
        """
        :param figsize: Figure size in inches (width, height).

        :param dpi: The dots per inch of the figure.
        """
        super().__init__()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        self.figure = Figure(figsize=figsize, dpi=dpi)
        self.axes = self.figure.add_subplot()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = Toolbar(self.canvas)

        layout = QVBoxLayout()
        self.setLayout(layout)
        add_to_layout(layout, self.canvas, self.toolbar)

    def resizeEvent(self, event: QResizeEvent | None):  # overridden method
        self.figure.tight_layout()
        return super().resizeEvent(event)

    def draw(self):
        self.canvas.draw()
