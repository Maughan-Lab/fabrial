from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout

from ..classes.actions import Shortcut
from ..classes.plotting import LineSettings
from ..classes.signals import GraphSignals
from ..custom_widgets.augmented.widget import Widget
from ..custom_widgets.plot import PlotWidget
from ..secondary_window import SecondaryWindow


class SequenceDisplayTab(Widget):
    """
    Tab for displaying widgets from the sequence runtime. This should only ever hold one widget at a
    time.
    """

    poppedGraphChanged = pyqtSignal(bool)
    """
    Fires when the graph is popped/unpopped. Sends a **bool** indicating whether the graph is
    popped.
    """

    def __init__(self):
        layout = QVBoxLayout()
        super().__init__(layout)
        self.plot = PlotWidget()
        layout.addWidget(self.plot)
        # create popped graph
        self.popped_graph = SecondaryWindow("Quincy - Sequence Graph", None, None)
        self.popped_graph.closed.connect(lambda: self.poppedGraphChanged.emit(False))
        # close the window on "Ctrl+g"
        Shortcut(self.popped_graph, "Ctrl+g", self.popped_graph.close)
        # save the graph on "Ctrl+s"
        Shortcut(self.plot, "Ctrl+s", self.plot.save_as_image)

    def connect_graph_signals(self, signals: GraphSignals):
        """Connect to the provided graph signals."""
        plot_item = self.plot.plot_item()
        signals.initPlot.connect(self.init_plot)
        signals.clear.connect(plot_item.reset)
        signals.addPoint.connect(plot_item.add_point)
        signals.saveFig.connect(self.plot.plot_view().export_to_image)
        signals.setLogScale.connect(plot_item.setLogMode)

    def init_plot(self, settings: LineSettings):
        """Initialize the plot."""
        plot_item = self.plot.plot_item()
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
