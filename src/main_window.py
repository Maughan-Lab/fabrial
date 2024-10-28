from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget
from setpoint.widgets import SetpointWidget
from passive_monitoring.widgets import PassiveMonitoringWidget
from instrument_connection.widgets import InstrumentConnectionWidget
from stability_check.widgets import StabilityCheckWidget
from temperature_sequence.widgets import SequenceWidget
from graph.widgets import GraphWidget
from instruments import InstrumentSet
from helper_functions.layouts import add_to_layout_grid


class MainWindow(QMainWindow):
    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setWindowTitle("Quincy")

        layout = QGridLayout()
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.setpoint_widget = SetpointWidget(instruments)
        self.passive_monitoring_widget = PassiveMonitoringWidget(instruments)
        self.instrument_connection_widget = InstrumentConnectionWidget(instruments)
        self.stability_check_widget = StabilityCheckWidget(instruments)
        self.sequence_widget = SequenceWidget(instruments)
        self.graph_widget = GraphWidget(instruments, self.sequence_widget.sequence_data)

        add_to_layout_grid(
            layout,
            (self.setpoint_widget, 0, 0),
            (self.stability_check_widget, 1, 0),
            (self.passive_monitoring_widget, 0, 1),
            (self.instrument_connection_widget, 0, 2),
            (self.sequence_widget, 2, 0),
        )
        layout.addWidget(self.graph_widget, 1, 1, 2, 2)
