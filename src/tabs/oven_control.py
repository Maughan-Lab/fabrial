from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..instrument_connection.widgets import InstrumentConnectionWidget
from ..passive_monitoring.widgets import PassiveMonitoringWidget
from ..setpoint.widgets import SetpointWidget
from ..stability_check.widgets import StabilityCheckWidget
from ..utility.layouts import add_sublayout, add_to_layout


class OvenControlTab(QWidget):
    """First tab in the application, used for directly controlling the oven."""

    def __init__(self) -> None:
        # data members
        self.setpoint_widget: SetpointWidget
        self.passive_monitoring_widget: PassiveMonitoringWidget
        self.instrument_connection_widget: InstrumentConnectionWidget
        self.stability_widget: StabilityCheckWidget

        super().__init__()

        self.create_widgets()

    def create_widgets(self):
        """Create subwidgets."""
        # create the layout
        layout = QVBoxLayout()
        top_layout = add_sublayout(layout, QHBoxLayout)
        self.setLayout(layout)

        self.setpoint_widget = SetpointWidget()
        self.stability_widget = StabilityCheckWidget()
        # do not move these two above the other ones
        self.passive_monitoring_widget = PassiveMonitoringWidget()
        self.instrument_connection_widget = InstrumentConnectionWidget()
        # add the widgets
        add_to_layout(
            top_layout,
            self.setpoint_widget,
            self.passive_monitoring_widget,
            self.instrument_connection_widget,
        )
        layout.addWidget(self.stability_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
