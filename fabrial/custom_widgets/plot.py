import typing
from typing import Literal

import pyqtgraph as pg
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QFileDialog, QHBoxLayout, QVBoxLayout
from pyqtgraph.exporters import ImageExporter

from ..classes import Shortcut
from ..plotting import LineData, LineParams, SymbolParams
from ..utility import errors, layout as layout_util
from .augmented import Button, Widget


def get_text_color() -> QColor:
    """Get the application's current text color."""
    return QApplication.palette().windowText().color()


def get_background_color() -> QColor:
    """Get the application's current background color."""
    return QApplication.palette().window().color()


class PlotItem(pg.PlotItem):
    """Plot item that automatically uses the OS color theme. This is not the widget."""

    LABEL_SIZE = "14pt"
    TITLE_SIZE = "20pt"
    DEFAULT_POINT_SIZE = 7

    def __init__(self) -> None:
        """Create a new PlotItem."""
        pg.PlotItem.__init__(self)
        self.lines: list[LineData] = []
        self.init_plot()

    def init_plot(self):
        """Initialize the plot during construction."""
        self.getViewBox().setBackgroundColor(get_background_color())
        self.addLegend()
        typing.cast(pg.LegendItem, self.legend).setLabelTextColor(get_text_color())
        self.recolor_axis("left")
        self.recolor_axis("bottom")

    def recolor_axis(self, axis_name: Literal["left", "right", "bottom", "top"]):
        """Recolor an axis during construction."""
        axis: pg.AxisItem = self.getAxis(axis_name)
        text_color = get_text_color()
        axis.setPen(text_color)
        axis.setTextPen(text_color)

    def set_label(
        self, axis_name: Literal["left", "right", "bottom", "top"], label: str | None, **kwargs
    ):
        """Set the label text for an axis."""
        axis: pg.AxisItem = self.getAxis(axis_name)
        axis.setLabel(label, **{"font-size": self.LABEL_SIZE}, **kwargs)

    def set_title(self, title: str | None, **kwargs):
        """Set the plot's title."""
        self.setTitle(title, size=self.TITLE_SIZE, color=get_text_color(), **kwargs)

    def reset(self):
        """Reset the plot to it's original state."""
        self.clear()
        for axis_name in ("left", "right", "top", "bottom"):
            self.set_label(axis_name, None)
        self.set_title(None)
        self.setLogMode(False, False)

    def line_count(self) -> int:
        """Get the number of lines on this item."""
        return len(self.lines)

    def plot(
        self,
        x_data: list[float],
        y_data: list[float],
        legend_label: str | None,
        line_params: LineParams | None,
        symbol_params: SymbolParams | None,
    ) -> LineData:
        """
        Plot a new line on top of the current lines. Stores the plotted item internally.

        Parameters
        ----------
        x_data
            The x-data.
        y_data
            The y-data.
        legend_label
            The label for this line in the legend. Can be `None` for no legend entry.
        line_params
            How the line should look. If `None` there will be no line.
        symbol_params
            How the symbols should look. If `None` there will be no symbols.

        Returns
        -------
        A reference to the plotted data.
        """
        if line_params is None:
            line_pen = None
        else:
            line_pen = pg.mkPen(line_params.color, width=line_params.width)
        if symbol_params is not None:  # if there should be symbols, plot with symbols
            line = pg.PlotItem.plot(
                self,
                x_data,
                y_data,
                name=legend_label,
                pen=line_pen,
                symbol=symbol_params.symbol,
                symbolSize=symbol_params.size,
                symbolBrush=symbol_params.color,
                symbolPen=pg.mkPen(color=symbol_params.color),
            )
        else:  # otherwise plot without symbols
            line = pg.PlotItem.plot(self, x_data, y_data, name=legend_label, pen=line_pen)

        line_data = LineData(line, x_data, y_data)
        self.lines.append(line_data)
        return line_data

    def add_point(self, x: float, y: float, line_index: int):
        """
        Add a point to the line at **line_index**.

        Raises
        ------
        IndexError
            **line_index** is out of range.
        """
        self.lines[line_index].add_point(x, y)

    def export_to_image(self, file: str):
        """Export the item to an image. This uses the item's current dimensions."""
        exporter = ImageExporter(self)
        exporter.export(file)


class PlotView(pg.PlotWidget):
    """Container for a PlotItem. Capable of exporting itself as an image."""

    def __init__(self):
        """Create a new PlotView."""
        self.plot_item = PlotItem()
        pg.PlotWidget.__init__(self, background=get_background_color(), plotItem=self.plot_item)


class PlotWidget(Widget):
    """Contains a `PlotView` and buttons for interacting with it."""

    def __init__(self):
        layout = QVBoxLayout()
        Widget.__init__(self, layout)
        self.view = PlotView()
        layout.addWidget(self.view)

        autoscale_button = Button("Autoscale", self.autoscale)
        Shortcut(self, "Ctrl+S", self.save_as_image)
        save_button = Button("Save", self.save_as_image)
        layout_util.add_to_layout(
            layout_util.add_sublayout(layout, QHBoxLayout()), autoscale_button, save_button
        )

    def save_as_image(self):
        file, _ = QFileDialog.getSaveFileName(
            None, "Save Graph", "untitled.png", "Portable Network Graphics (*.png)"
        )
        if file != "":
            try:
                self.view.plot_item.export_to_image(file)
            except Exception:
                errors.show_error("Save Error", "Failed to save graph.")

    def autoscale(self):
        """Autoscale the graph."""
        self.view.plot_item.getViewBox().enableAutoRange(pg.ViewBox.XYAxes)
