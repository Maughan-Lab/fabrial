from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFileDialog
from ..utility.layouts import add_to_layout, add_sublayout
import pyqtgraph as pg  # type: ignore
import pyqtgraph.exporters as exporters  # type: ignore
from ..custom_widgets.button import Button
from ..custom_widgets.widget import SignalWidget, Widget
from typing import Literal


class PlotItem(pg.PlotItem):
    """Plot item that automatically uses the OS color theme. This is not the widget."""

    LABEL_SIZE = "14pt"
    TITLE_SIZE = "20pt"

    def __init__(self) -> None:
        """Create a new PlotItem."""
        super().__init__()
        self.text_color = self.palette().windowText().color().name()
        self.background_color = self.palette().window().color().name()

        self.create_plot()

    def create_plot(self):
        self.getViewBox().setBackgroundColor(self.background_color)
        self.addLegend()
        self.legend.setLabelTextColor(self.text_color)
        self.recolor_axis("left")
        self.recolor_axis("bottom")

    def recolor_axis(self, axis_name: Literal["left", "right", "bottom", "top"]):
        axis: pg.AxisItem = self.getAxis(axis_name)
        axis.setPen(self.text_color)
        axis.setTextPen(self.text_color)

    def label(self, axis_name: Literal["left", "right", "bottom", "top"], label: str, **args):
        axis: pg.AxisItem = self.getAxis(axis_name)
        axis.setLabel(label, **{"font-size": self.LABEL_SIZE}, **args)

    def set_title(self, title: str, **args):
        self.setTitle(title, size=self.TITLE_SIZE, color=self.text_color, **args)

    def scatter(
        self,
        x_data: list[float | int],
        y_data: list[float | int],
        name: str,
        point_size: int,
        point_color: str,
        **args,
    ) -> pg.PlotDataItem:
        """
        Plot a scatterplot on a **PlotItem**.

        :param plot_item: The PlotItem to plot on.
        :param x_data: The x-data.
        :param y_data: The y-data.
        :param name: The label for this line in the legend.
        :param point_size: The point size.
        :param point_color: The color of the points. Can be a hex string (i.e. "#112233") or a standard
        color name (i.e. "green").
        :param args: Additional arguments to pass to **PlotItem.plot()**.

        :returns: A reference to the plotted line.
        """
        line = self.plot(
            x_data,
            y_data,
            name=name,
            pen=None,
            symbol="o",
            symbolSize=point_size,
            symbolBrush=point_color,
            symbolPen=pg.mkPen(color=point_color),
        )
        return line


class PlotView(pg.PlotWidget):
    """Container for a PlotItem. Capable of exporting itself as an image."""

    def __init__(self):
        """Create a new PlotView."""
        plot_item = PlotItem()
        super().__init__(background=plot_item.background_color, plotItem=plot_item)

    def export_to_image(self, filename: str):
        exporter = exporters.ImageExporter(self.getPlotItem())
        exporter.export(filename)


class PlotWidget(Widget):
    """Contains a **PlotView** and buttons for interacting with it."""

    def __init__(self):
        layout = QVBoxLayout()
        super().__init__(layout)
        self.view = PlotView()
        layout.addWidget(self.view)

        autoscale_button = Button("Autoscale", self.autoscale)
        save_button = Button("Save", self.save_as_image)
        add_to_layout(add_sublayout(layout, QHBoxLayout), autoscale_button, save_button)

    def plot_item(self) -> PlotItem:
        """Get the underlying **PlotItem**."""
        return self.view.getPlotItem()

    def save_as_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            None, "Save Graph", "", "Portable Network Graphics (*.png)"
        )
        if filename != "":
            self.export_to_image(filename)

    def autoscale(self):
        """Autoscale the graph."""
        self.plot_item().getViewBox().enableAutoRange(pg.ViewBox.XYAxes)


class OldPlotWidget(SignalWidget):
    """Plot widget for displaying data. This is the widget."""

    def __init__(self, plot_container: PlotView | None = None):
        """
        Create a new PlotWidget. Optionally provide a **PlotContainer** to initialize this widget
        with.
        """
        super().__init__()
        self.plot_item: PlotItem
        self.plot_container: PlotView

        if plot_container is not None:
            self.plot_container = plot_container
            self.plot_item = plot_container.getPlotItem()
        else:
            self.plot_container = PlotView()
            self.plot_item = self.plot_container.getPlotItem()

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(self.plot_container)

        autoscale_button = Button("Autoscale", self.autoscale)
        save_button = Button("Save", self.save_as_image)
        button_layout = add_sublayout(layout, QHBoxLayout)
        add_to_layout(button_layout, autoscale_button, save_button)

    def autoscale(self):
        """Autoscale the graph."""
        self.plot_item.getViewBox().enableAutoRange(pg.ViewBox.XYAxes)

    def save_as_image(self):
        filename, _ = QFileDialog.getSaveFileName(
            None, "Save Graph", "", "Portable Network Graphics (*.png)"
        )
        if filename != "":
            self.plot_container.export_to_image(filename)
