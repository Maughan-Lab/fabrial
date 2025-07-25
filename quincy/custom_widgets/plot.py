from typing import Literal

import pyqtgraph as pg  # type: ignore
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout
from pyqtgraph.exporters import ImageExporter  # type: ignore

from ..classes import LineData
from ..utility import layout as layout_util
from .augmented import Button, OkDialog, Widget


class PlotItem(pg.PlotItem):
    """Plot item that automatically uses the OS color theme. This is not the widget."""

    LABEL_SIZE = "14pt"
    TITLE_SIZE = "20pt"
    DEFAULT_POINT_SIZE = 7

    def __init__(self) -> None:
        """Create a new PlotItem."""
        pg.PlotItem.__init__(self)
        self.text_color = self.palette().windowText().color().name()
        self.background_color = self.palette().window().color().name()
        self.line_data: LineData
        self.init_plot()

    def init_plot(self):
        self.getViewBox().setBackgroundColor(self.background_color)
        self.addLegend()
        self.legend.setLabelTextColor(self.text_color)  # type: ignore
        self.recolor_axis("left")
        self.recolor_axis("bottom")

    def recolor_axis(self, axis_name: Literal["left", "right", "bottom", "top"]):
        axis: pg.AxisItem = self.getAxis(axis_name)
        axis.setPen(self.text_color)
        axis.setTextPen(self.text_color)

    def label(
        self, axis_name: Literal["left", "right", "bottom", "top"], label: str | None, **args
    ):
        axis: pg.AxisItem = self.getAxis(axis_name)
        axis.setLabel(label, **{"font-size": self.LABEL_SIZE}, **args)

    def set_title(self, title: str | None, **args):
        self.setTitle(title, size=self.TITLE_SIZE, color=self.text_color, **args)

    def current_line(self) -> pg.PlotDataItem:
        """Get the current line."""
        return self.line_data.line

    def reset(self):
        """Reset the plot to it's original state."""
        self.clear()
        for axis_name in ("left", "right", "top", "bottom"):
            self.label(axis_name, None)
        self.set_title(None)
        self.setLogMode(False, False)

    def plot(
        self,
        x_data: list[float],
        y_data: list[float],
        legend_label: str,
        line_color: str | None,
        line_width: float | None,
        symbol: str,
        symbol_color: str,
        symbol_size: int,
    ):
        """
        Plot a new line.

        :param x_data: The x-data.
        :param y_data: The y-data.
        :param legend_label: The label for this line in the legend.
        :param line_color: The color of the line. If set to **None**, there will be no line.
        :param line_width: The width of the line. If set to **None**, there will be no line.
        :param symbol: The symbol to use, i.e. "o" for a dot.
        :param symbol_size: The point size.
        :param symbol_color: The color of the points. Can be a hex string (i.e. "#112233") or a
        standard color name (i.e. "green").

        :returns: A reference to the data item.
        """
        if line_color is None or line_width is None:
            line_pen = None
        else:
            line_pen = pg.mkPen(line_color, width=line_width)
        data_item = pg.PlotItem.plot(
            self,
            x_data,
            y_data,
            name=legend_label,
            pen=line_pen,
            symbol=symbol,
            symbolSize=symbol_size,
            symbolBrush=symbol_color,
            symbolPen=pg.mkPen(color=symbol_color),
        )
        self.line_data = LineData(data_item, x_data, y_data)

    def add_point(self, x_value: float, y_value: float):
        """
        Add a point to the current line. You must call `plot()` before this function.
        """
        self.line_data.add_point(x_value, y_value)


class PlotView(pg.PlotWidget):
    """Container for a PlotItem. Capable of exporting itself as an image."""

    def __init__(self):
        """Create a new PlotView."""
        plot_item = PlotItem()
        pg.PlotWidget.__init__(self, background=plot_item.background_color, plotItem=plot_item)

    def export_to_image(self, filename: str):
        """Export the image. This uses the image's current dimensions."""
        exporter = ImageExporter(self.getPlotItem())
        exporter.export(filename)


class PlotWidget(Widget):
    """Contains a **PlotView** and buttons for interacting with it."""

    def __init__(self):
        layout = QVBoxLayout()
        Widget.__init__(self, layout)
        self.view = PlotView()
        layout.addWidget(self.view)

        autoscale_button = Button("Autoscale", self.autoscale)
        save_button = Button("Save", self.save_as_image)
        layout_util.add_to_layout(
            layout_util.add_sublayout(layout, QHBoxLayout), autoscale_button, save_button
        )

    def plot_item(self) -> PlotItem:
        """Get the underlying **PlotItem**."""
        return self.view.getPlotItem()

    def plot_view(self) -> PlotView:
        """Get the underlying **PlotView**."""
        return self.view

    def save_as_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            None, "Save Graph", "untitled.png", "Portable Network Graphics (*.png)"
        )
        if filename != "":
            try:
                self.view.export_to_image(filename)
            except Exception:
                OkDialog("Error", "Failed to save graph.")

    def autoscale(self):
        """Autoscale the graph."""
        self.plot_item().getViewBox().enableAutoRange(pg.ViewBox.XYAxes)
