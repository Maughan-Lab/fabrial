from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout

from ..classes.actions import Shortcut
from ..classes.plotting import LineSettings
from ..classes.signals import GraphSignals
from ..custom_widgets.augmented.widget import Widget
from ..custom_widgets.plot import PlotWidget
from ..secondary_window import SecondaryWindow


class SequenceDisplayTab(QTabWidget):
    """
    Tab for displaying widgets from the sequence runtime. This should only ever hold one widget at a
    time.
    """

    poppedGraphChanged = pyqtSignal(bool)
    """
    Fires when the graph is popped/unpopped. Sends a **bool** indicating whether the graph is
    popped.
    """

    def __init__(self) -> None:
        super().__init__()
        self.plots: list[PlotWidget] = []

        # create popped graph
        self.popped_graph = SecondaryWindow("Quincy - Sequence Graph", None, None)
        self.popped_graph.closed.connect(lambda: self.poppedGraphChanged.emit(False))
        # TODO: fix these
        # close the window on "Ctrl+g"
        # Shortcut(self.popped_graph, "Ctrl+g", self.popped_graph.close)
        # save the graph on "Ctrl+s"
        # Shortcut(self.plot, "Ctrl+s", self.plot.save_as_image)

    def connect_graph_signals(self, signals: GraphSignals):
        """Connect to the provided graph signals."""
        signals.initPlot.connect(self.init_plot)
        signals.reset.connect(self.reset)
        signals.clear.connect(self.clear_plot)
        signals.addPoint.connect(self.add_point)
        signals.saveFig.connect(self.save_figure)
        signals.setLogScale.connect(self.set_log_scale)

    def init_plot(self, index: int, settings: LineSettings):
        """Initialize the plot."""

        # TODO: you also need to send an identifier for the name of the graph

        if self.count() < index:
            raise IndexError(
                "Attempted to create plot at an invalid index. "
                f"Index was {index} but length of plot list is {len(self.plots)}"
            )
        elif index == self.count():  # we're making a new plot
            plot = PlotWidget()
            self.addTab(plot, str(index))
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
        self.plots.clear()

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
        self.poppedGraphChanged.emit(True)
        self.popped_graph.setCentralWidget(self.plot)
        self.popped_graph.closed.connect(lambda: self.layout().addWidget(self.plot))
        self.popped_graph.show()

    def unpop_graph(self):
        """Unpop the graph."""
        self.popped_graph.close()
        self.poppedGraphChanged.emit(False)
