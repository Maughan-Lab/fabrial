from PyQt6.QtWidgets import QHBoxLayout, QWidget
from ..utility.layouts import add_to_layout
from ..setpoint.widgets import SetpointWidget
from ..passive_monitoring.widgets import PassiveMonitoringWidget
from ..instrument_connection.widgets import InstrumentConnectionWidget


class OvenControlTab(QWidget):
    """First tab in the application, used for directly controlling the oven."""

    def __init__(self) -> None:
        # data members
        self.setpoint_widget: SetpointWidget
        self.passive_monitoring_widget: PassiveMonitoringWidget
        self.instrument_connection_widget: InstrumentConnectionWidget

        super().__init__()

        self.create_widgets()

    def create_widgets(self):
        """Create subwidgets."""
        # create the layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.initialize_widgets()
        # add the widgets
        add_to_layout(
            layout,
            self.setpoint_widget,
            self.passive_monitoring_widget,
            self.instrument_connection_widget,
        )

    def initialize_widgets(self):  # this is necessary for testing
        """Store subwidgets in variables."""
        self.setpoint_widget = SetpointWidget()
        # do not move these two above the other ones
        self.passive_monitoring_widget = PassiveMonitoringWidget()
        self.instrument_connection_widget = InstrumentConnectionWidget()
