from PyQt6.QtWidgets import QMainWindow, QGridLayout, QWidget
from setpoint.widgets import SetpointWidget
from passive_monitoring.widgets import PassiveMonitoringWidget
from instrument_connection.widgets import InstrumentConnectionWidget
from stability_check.widgets import StabilityCheckWidget
from temperature_sequence.widgets import SequenceWidget
from instruments import InstrumentSet


class MainWindow(QMainWindow):
    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setWindowTitle("Quincy")

        layout = QGridLayout()

        central_widget = QWidget()
        central_widget.setLayout(layout)

        layout.addWidget(SetpointWidget(instruments))
        self.passive_monitoring_widget = PassiveMonitoringWidget(instruments)
        layout.addWidget(self.passive_monitoring_widget)
        self.instrument_connection_widget = InstrumentConnectionWidget(instruments)
        layout.addWidget(self.instrument_connection_widget)
        self.stability_check_widget = StabilityCheckWidget(instruments)
        layout.addWidget(self.stability_check_widget)
        self.sequence_widget = SequenceWidget(instruments)
        layout.addWidget(self.sequence_widget)

        self.setCentralWidget(central_widget)
