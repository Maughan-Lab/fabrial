from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..instrument_connection import InstrumentConnectionWidget
from ..passive_monitoring import PassiveMonitoringWidget
from ..setpoint import SetpointWidget
from ..stability_check import StabilityCheckWidget
from ..utility import layout as layout_util


class OvenControlTab(QWidget):
    """First tab in the application, used for directly controlling the oven."""

    ICON_FILE = "thermometer.png"

    def __init__(self) -> None:
        # data members
        self.setpoint_widget: SetpointWidget
        self.passive_monitoring_widget: PassiveMonitoringWidget
        self.instrument_connection_widget: InstrumentConnectionWidget
        self.stability_widget: StabilityCheckWidget

        QWidget.__init__(self)

        self.create_widgets()

    def create_widgets(self):
        """Create subwidgets."""
        # create the layout
        layout = QVBoxLayout()
        top_layout = layout_util.add_sublayout(layout, QHBoxLayout())
        self.setLayout(layout)

        self.setpoint_widget = SetpointWidget()
        self.stability_widget = StabilityCheckWidget()
        # do not move these two above the other ones
        self.passive_monitoring_widget = PassiveMonitoringWidget()
        self.instrument_connection_widget = InstrumentConnectionWidget()
        # add the widgets
        layout_util.add_to_layout(
            top_layout,
            self.setpoint_widget,
            self.passive_monitoring_widget,
            self.instrument_connection_widget,
        )
        layout.addWidget(self.stability_widget, alignment=Qt.AlignmentFlag.AlignHCenter)
