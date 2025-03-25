from PyQt6.QtWidgets import QGridLayout, QWidget
from setpoint.widgets import SetpointWidget
from passive_monitoring.widgets import PassiveMonitoringWidget
from instrument_connection.widgets import InstrumentConnectionWidget
from stability_check.widgets import StabilityCheckWidget
from sequence.widgets import SequenceWidget
from graph.widgets import GraphWidget
from utility.layouts import add_to_layout_grid
from instruments import InstrumentSet
from secondary_window import SecondaryWindow
from classes.actions import Shortcut
from custom_widgets.plot import PlotWidget


class OvenControlTab(QWidget):
    def __init__(self, instruments: InstrumentSet) -> None:
        # data members
        self.setpoint_widget: SetpointWidget
        self.stability_check_widget: StabilityCheckWidget
        self.sequence_widget: SequenceWidget
        self.graph_widget: GraphWidget
        self.passive_monitoring_widget: PassiveMonitoringWidget
        self.instrument_connection_widget: InstrumentConnectionWidget
        self.popped_graph: SecondaryWindow

        super().__init__()

        self.create_widgets(instruments)
        self.create_popped_graph(self.graph_widget.plot)
        self.connect_signals()

    def create_widgets(self, instruments):
        """Create subwidgets."""
        # create the layout
        layout = QGridLayout()
        self.setLayout(layout)

        self.initialize_widgets(instruments)
        # add the widgets
        add_to_layout_grid(
            layout,
            (self.setpoint_widget, 0, 0),
            (self.stability_check_widget, 1, 0),
            (self.passive_monitoring_widget, 0, 1),
            (self.instrument_connection_widget, 0, 2),
            (self.sequence_widget, 2, 0),
        )
        layout.addWidget(self.graph_widget, 1, 1, 2, 2)

    def initialize_widgets(self, instruments: InstrumentSet):  # this is necessary for testing
        """Store subwidgets in variables."""
        self.setpoint_widget = SetpointWidget(instruments)
        self.stability_check_widget = StabilityCheckWidget(instruments)
        self.sequence_widget = SequenceWidget(instruments)
        self.graph_widget = GraphWidget()
        # do not move these two above the other ones
        self.passive_monitoring_widget = PassiveMonitoringWidget(instruments)
        self.instrument_connection_widget = InstrumentConnectionWidget(instruments)

    def create_popped_graph(self, plot: PlotWidget):
        self.popped_graph = SecondaryWindow("Quincy - Popped Graph", None)
        # close the window on "Ctrl+g"
        Shortcut(self.popped_graph, "Ctrl+g", self.popped_graph.close)
        # save the graph on "Ctrl+s"
        Shortcut(self.popped_graph, "Ctrl+s", plot.save_as_image)
        # return the graph widget to its previous state on PoppedGraph destruction
        self.popped_graph.closed.connect(lambda: self.graph_widget.give_widget(plot))
        self.popped_graph.closed.connect(self.graph_widget.show)

    def connect_signals(self):
        """Connect widget signals."""
        # connect the graph
        self.sequence_widget.newDataAquired.connect(self.graph_widget.add_point)
        self.sequence_widget.cycleNumberChanged.connect(self.graph_widget.move_to_next_cycle)
        self.sequence_widget.stageChanged.connect(self.graph_widget.handle_stage_change)

    # ----------------------------------------------------------------------------------------------
    # pop the graph
    def pop_graph(self):
        """Pop the sequence graph into a new window."""
        self.graph_widget.hide()
        plot = self.graph_widget.plot
        self.popped_graph.setCentralWidget(plot)
        self.popped_graph.show()

    def unpop_graph(self):
        """Put the sequence graph back into the main window by closing the PoppedGraph."""
        self.popped_graph.close()
