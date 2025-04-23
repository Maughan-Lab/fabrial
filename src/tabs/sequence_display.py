from PyQt6.QtWidgets import QVBoxLayout
from ..custom_widgets.widget import Widget
from ..custom_widgets.plot import PlotWidget
from ..classes.signals import GraphSignals
from ..classes.plotting import LineSettings


class SequenceDisplayTab(Widget):
    """
    Tab for displaying widgets from the sequence runtime. This should only ever hold one widget at a
    time.
    """

    def __init__(self):
        layout = QVBoxLayout()
        super().__init__(layout)
        self.plot = PlotWidget()
        layout.addWidget(self.plot)

    def connect_graph_signals(self, signals: GraphSignals):
        plot_item = self.plot.plot_item()
        signals.initPlot.connect(self.init_plot)
        signals.clear.connect(plot_item.reset)
        signals.addPoint.connect(plot_item.add_point)

    def init_plot(self, settings: LineSettings):
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
