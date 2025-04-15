from PyQt6.QtWidgets import QVBoxLayout
from ..custom_widgets.widget import Widget
from ..custom_widgets.plot import PlotWidget
from ..classes.signals import GraphSignals


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
        # TODO: connect all possible graph signals to functions on the PlotWidget
        pass
