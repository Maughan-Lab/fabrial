from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTabWidget

from ..classes.actions import Shortcut
from ..classes.plotting import LineSettings
from ..classes.signals import GraphSignals
from ..custom_widgets.augmented.button import Button
from ..custom_widgets.plot import PlotWidget
from ..secondary_window import SecondaryWindow


class SequenceDisplayTab(QTabWidget):
    """
    Tab for displaying widgets from the sequence runtime. This should only ever hold one widget at a
    time.
    """

    def __init__(self) -> None:
        super().__init__()
        self.plots: list[PlotWidget] = []
        self.popped_graphs: list[SecondaryWindow] = []

        self.setCornerWidget(Button("Pop Graph", self.pop_graph), Qt.Corner.TopRightCorner)
        self.setMovable(True)
        Shortcut(self, "Ctrl+G", self.pop_graph)

    def connect_graph_signals(self, signals: GraphSignals):
        """Connect to the provided graph signals."""
        signals.initPlot.connect(self.init_plot)
        signals.reset.connect(self.reset)
        signals.clear.connect(self.clear_plot)
        signals.addPoint.connect(self.add_point)
        signals.saveFig.connect(self.save_figure)
        signals.setLogScale.connect(self.set_log_scale)

    def init_plot(self, index: int, name: str, settings: LineSettings):
        """Initialize the plot."""
        if self.count() < index:
            raise IndexError(
                "Attempted to create plot at an invalid index. "
                f"Index was {index} but length of plot list is {len(self.plots)}"
            )
        elif index == self.count():  # we're making a new plot
            plot = PlotWidget()
            Shortcut(plot, "Ctrl+S", plot.save_as_image)
            self.addTab(plot, name)
            self.plots.append(plot)
        else:  # we're modifying an existing plot
            plot = self.plots[index]

        plot_item = plot.plot_item()
        plot_item.set_title(settings.title)
        plot_item.label("bottom", settings.x_label)
        plot_item.label("left", settings.y_label)
        plot_item.plot(
            [],
            [],
            settings.legend_label,
            settings.line_color,
            settings.line_width,
            settings.symbol,
            settings.symbol_color,
            settings.symbol_size,
        )

    def reset(self):
        """Destroy all plots."""
        while self.count() > 0:
            tab = self.widget(0)
            self.removeTab(0)
            if tab is not None:
                tab.deleteLater()
        for popped_graph in self.popped_graphs:
            popped_graph.close_silent()
            popped_graph.deleteLater()
        self.plots.clear()
        self.popped_graphs.clear()

    def clear_plot(self, index: int):
        """Clear a plot."""
        self.plots[index].plot_item().reset()

    def add_point(self, index: int, x_value: float, y_value: float):
        """Add a point to the plot at **index**."""
        self.plots[index].plot_item().add_point(x_value, y_value)

    def save_figure(self, index: int, filepath: str):
        """Save the plot at **index** to **filepath**."""
        self.plots[index].plot_view().export_to_image(filepath)

    def set_log_scale(self, index: int, x_log: bool | None, y_log: bool | None):
        """Set the whether the plot at **index** uses a log scale."""
        self.plots[index].plot_item().setLogMode(x_log, y_log)

    def pop_graph(self):
        """Pop the graph into a secondary window."""
        plot = self.currentWidget()
        if plot is not None:
            tab_title = self.tabText(self.currentIndex())
            popped_window = SecondaryWindow(tab_title, plot)
            Shortcut(popped_window, "Ctrl+G", popped_window.close)
            self.popped_graphs.append(popped_window)

            popped_window.closed.connect(lambda: self.popped_graphs.remove(popped_window))
            popped_window.closed.connect(lambda: self.addTab(plot, tab_title))

            popped_window.show()
            popped_window.resize(popped_window.sizeHint())
