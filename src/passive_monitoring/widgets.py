from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet  # ../instruments.py
from utility.new_timer import new_timer_nostart  # ../utility


class PassiveMonitoringWidget(GroupBox):
    """Widget for monitoring the oven."""

    NULL_TEXT = "-----"

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Measurements", QGridLayout, instruments)

        self.create_widgets()

        # timer to update the oven temperature, setpoint, and status every second
        self.update_timer = new_timer_nostart(1000, self.monitor)
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
        # category_label.setFont(font)
        label_widget.setFont(font)

        layout.addWidget(category_label, row, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(label_widget, row, 1)

    def connect_signals(self):
        self.instruments.oven.connectionChanged.connect(self.handle_connection_change)

    def handle_connection_change(self, connected: bool):
        # only monitor the oven when it is connected
        if connected:
            self.update_timer.start()
        else:
            self.handle_disconnect()

    def handle_disconnect(self):
        for label in (self.temperature_label, self.setpoint_label):
            label.setText(self.NULL_TEXT)
        self.update_timer.stop()

    def update_label(self, label: Label, value: float):
        label.setText(str(value))

    def monitor(self):
        temperature = self.instruments.oven.read_temp()
        if temperature is None:
            return
        self.update_label(self.temperature_label, temperature)

        setpoint = self.instruments.oven.get_setpoint()
        if setpoint is None:
            return
        self.update_label(self.setpoint_label, setpoint)
