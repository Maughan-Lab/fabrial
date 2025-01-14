from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtGui import QResizeEvent
from .container import Container
from utility.layouts import add_to_layout  # ../utility
import matplotlib
from matplotlib.backends.backend_qtagg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QT,
)
from matplotlib.figure import Figure
from matplotlib.patches import Patch

matplotlib.use("QtAgg")


class Toolbar(NavigationToolbar2QT):
    """Toolbar with some altered commands."""

    def __init__(self, canvas, parent=None, coordinates=True):
        super().__init__(canvas, parent, coordinates)

    def home(self, *args):  # overridden method
        self.canvas.figure.tight_layout()
        super().home(*args)


class PlotWidget(Container):
    """Plot class for displaying **matplotlib** plots."""

    def __init__(
        self, figure: Figure | None = None, figsize: tuple[int, int] = (6, 5), dpi: int = 100
    ):
        """
        :param figure: The figure to use inside this widget. Optional.
        :param figsize: Figure size in inches (width, height). Defaults to 6x5.
        :param dpi: The dots per inch of the figure. Defaults to 100.
        """
        super().__init__(QVBoxLayout)

        if figure is None:
            self.figure = Figure(figsize=figsize, dpi=dpi)
            self.axes = self.figure.add_subplot()
        else:
            self.figure = figure
            self.axes = figure.gca()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = Toolbar(self.canvas)

        layout = self.layout()
        layout.setSpacing(0)
        add_to_layout(layout, self.canvas, self.toolbar)

    def resizeEvent(self, event: QResizeEvent | None):  # overridden method
        self.figure.tight_layout()
        return super().resizeEvent(event)

    def clean(self):
        """Remove the data without modifying the axes labels or legend."""
        xlabel = self.axes.get_xlabel()
        ylabel = self.axes.get_ylabel()
        handles = self.axes.get_legend().get_patches()
        self.axes.clear()
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        self.axes.legend(handles=handles)

    # ----------------------------------------------------------------------------------------------
    # reexported methods
    def plot(self, *args, **kwargs):
        return self.axes.plot(*args, **kwargs)

    def scatter(self, x: float, y: float, **kwargs):
        return self.axes.scatter(x, y, **kwargs)

    def draw(self):
        self.canvas.draw()

    def set_title(self, title: str):
        self.axes.set_title(title)

    def set_xlabel(self, label: str):
        self.axes.set_xlabel(label)

    def set_ylabel(self, label: str):
        self.axes.set_ylabel(label)

    def tight_layout(self):
        self.figure.tight_layout()

    def legend(self, handles: tuple[Patch], fontsize: int | str):
        self.axes.legend(handles=handles, fontsize=fontsize)
