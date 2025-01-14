from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet  # ../instruments.py


class PassiveMonitoringWidget(GroupBox):
    """Widget for monitoring the oven."""

    NULL_TEXT = "-----"

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Measurements", QGridLayout, instruments)

        self.create_widgets()
        self.connect_signals()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.temperature_label = Label(self.NULL_TEXT)
        self.setpoint_label = Label(self.NULL_TEXT)

        self.add_widget_row(layout, "Temperature", 0, self.temperature_label)  # oven temperature
        self.add_widget_row(layout, "Setpoint", 1, self.setpoint_label)  # oven setpoint

    def add_widget_row(self, layout: QGridLayout, text: str, row: int, label_widget: Label):
        category_label = Label("Oven " + text + ":")

        font = QFont("Arial", 16)
        label_widget.setFont(font)

        layout.addWidget(category_label, row, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(label_widget, row, 1)

    def connect_signals(self):
        self.instruments.oven.connectionChanged.connect(self.handle_connection_change)
        self.instruments.oven.temperatureChanged.connect(self.handle_temperature_change)
        self.instruments.oven.setpointChanged.connect(self.handle_setpoint_change)

    def handle_connection_change(self, connected: bool):
        if not connected:
            self.handle_disconnect()

    def handle_disconnect(self):
        for label in (self.temperature_label, self.setpoint_label):
            label.setText(self.NULL_TEXT)

    def handle_temperature_change(self, temperature: float):
        self.update_label(self.temperature_label, temperature)

    def handle_setpoint_change(self, setpoint: float):
        self.update_label(self.setpoint_label, setpoint)

    def update_label(self, label: Label, value: float):
        label.setText(str(value))
