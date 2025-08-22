import logging
import typing
from os import PathLike

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTabWidget

from ..classes import DataLock, Shortcut
from ..custom_widgets import Button, PlotWidget
from ..plotting import LineIndex, LineParams, PlotIndex, PlotSettings, SymbolParams
from ..secondary_window import SecondaryWindow
from ..utility import images

ICON_FILENAME = "chart.png"


class SequenceDisplayTab(QTabWidget):
    """Tab for displaying graphing widgets during the sequence."""

    def __init__(self):
        QTabWidget.__init__(self)
        self.plots: list[PlotWidget] = []
        self.popped_graphs: dict[int, SecondaryWindow] = {}

        self.setCornerWidget(Button("Pop Graph", self.pop_graph), Qt.Corner.TopRightCorner)
        self.setMovable(True)  # allow moving tabs around
        Shortcut(self, "Ctrl+G", self.pop_graph)

        self.sequence_step_map: dict[int, tuple[QTabWidget, dict[int, PlotWidget]]] = {}

        self.step_tab_icon = images.make_icon("category.png")
        self.plot_tab_icon = images.make_icon("chart-up.png")

    def get_plot(self, plot_index: PlotIndex) -> PlotWidget:
        """
        Get the plot corresponding to **plot_index**.

        Raises
        ------
        IndexError
            The plot at **plot_index** does not exist. This is fatal.
        """
        # indexing goes
        # dict[int, tuple[QTabWidget, dict[int, PlotWidget]]]
        # tuple[QTabWidget, dict[int, PlotWidget]]
        # dict[int, PlotWidget]
        # PlotWidget
        return self.sequence_step_map[plot_index.step_address][1][plot_index.plot_number]

    def add_plot(
        self,
        step_address: int,
        step_name: str,
        tab_text: str,
        plot_settings: PlotSettings,
        receiver: DataLock[PlotIndex | None],
    ):
        """
        Create a new tab for the step at **step_address** (if there isn't one already), then create
        a plot in that tab. Sends a `PlotIndex` to the **receiver** that can be used to index the
        new plot later.
        """
        # get the plots map if it exists, otherwise create and add it
        try:
            step_tab_widget, plots = self.sequence_step_map[step_address]
        except KeyError:
            plots = {}
            step_tab_widget = QTabWidget()  # create a new tab widget for the plot
            step_tab_widget.setMovable(True)  # allow moving plot tabs around
            self.addTab(step_tab_widget, self.step_tab_icon, step_name)
            self.sequence_step_map[step_address] = (step_tab_widget, plots)

        # create and initialize the plot
        plot_widget = PlotWidget()
        plot_item = plot_widget.view.plot_item  # shortcut
        plot_item.set_title(plot_settings.title)
        plot_item.set_label("bottom", plot_settings.x_label)
        plot_item.set_label("left", plot_settings.y_label)
        # we can use the address because removing the plot from this widget is the same as deleting
        # the plot
        plot_number = id(plot_widget)
        plots[plot_number] = plot_widget
        # add the plot to the step's tab widget
        step_tab_widget.addTab(plot_widget, self.plot_tab_icon, tab_text)

        receiver.set(PlotIndex(step_address, plot_number))  # send the index to the receiver

    def remove_plot(self, plot_index: PlotIndex):
        """Remove and delete the plot at **plot_index**."""
        # remove the plot from the map
        plot_tab_widget, plot_map = self.sequence_step_map[plot_index.step_address]
        # remove the plot
        plot_widget = plot_map.pop(plot_index.plot_number)
        # un-pop the graph if it is popped
        if (popped_graph := self.popped_graphs.get(id(plot_widget))) is not None:
            popped_graph.close()
        plot_widget.setParent(None)
        plot_widget.deleteLater()
        # if there are no more plots, remove the entire tab
        if len(plot_map) == 0:
            self.sequence_step_map.pop(plot_index.step_address)  # remove from the map
            plot_tab_widget.setParent(None)
            plot_tab_widget.deleteLater()

    def add_line(
        self,
        plot_index: PlotIndex,
        legend_label: str | None,
        line_params: LineParams | None,
        symbol_params: SymbolParams | None,
        receiver: DataLock[LineIndex | None],
    ):
        """
        Add a new line to the plot at **plot_index** configured using **line_settings**. Sends a
        `LineIndex` to the **receiver** that can be used to index the new line later.
        """
        # create a new empty line
        plot_item = self.get_plot(plot_index).view.plot_item
        # we can use the line count as an index because you can't remove lines
        line_number = plot_item.line_count()  # store this before adding the new line
        plot_item.plot([], [], legend_label, line_params, symbol_params)
        receiver.set(LineIndex(plot_index, line_number))  # send the index to the receiver

    def add_point(self, line_index: LineIndex, x: float, y: float):
        """Add a point to the line at **line_index**."""
        self.get_plot(line_index.plot_index).view.plot_item.add_point(x, y, line_index.line_number)

    def set_log_scale(self, plot_index: PlotIndex, x_log: bool | None, y_log: bool | None):
        """Set the whether the plot at **plot_index** uses a log scale."""
        self.get_plot(plot_index).view.plot_item.setLogMode(x_log, y_log)

    def save_plot(self, plot_index: PlotIndex, file: PathLike[str] | str):
        """Save the plot at **plot_index** to **file**."""
        try:
            self.get_plot(plot_index).view.plot_item.export_to_image(str(file))
        except Exception:  # silently ignore the error and log it
            logging.getLogger(__name__).exception("Failed to save plot as image")

    def pop_graph(self):
        """Pop the current graph into a secondary window."""
        # this cast is safe because we only ever add `QTabWidget`s to this widget
        step_tab_widget = typing.cast(QTabWidget, self.currentWidget())
        if step_tab_widget is not None:
            plot = step_tab_widget.currentWidget()
            if plot is not None:
                tab_title = step_tab_widget.tabText(step_tab_widget.currentIndex())
                popped_window = SecondaryWindow(tab_title, plot)
                Shortcut(popped_window, "Ctrl+G", popped_window.close)
                plot_address = id(plot)
                self.popped_graphs[plot_address] = popped_window
                # closing the popped graph puts it back in its original parent
                popped_window.closed.connect(lambda: self.popped_graphs.pop(plot_address))
                popped_window.closed.connect(
                    lambda: step_tab_widget.addTab(plot, self.plot_tab_icon, tab_title)
                )
                # show and ensure the initial size is correct
                popped_window.show()
                popped_window.resize(popped_window.sizeHint())
