from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet  # ../instruments.py
from utility.new_timer import new_timer  # ../utility


class PassiveMonitoringWidget(GroupBox):
    """Widget for monitoring the oven."""

    # signals
    temperatureRead = pyqtSignal(float)
    setpointRead = pyqtSignal(float)

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Measurements", QGridLayout, instruments)

        self.create_widgets()
        self.connect_signals()

        # timer to update the oven temperature, setpoint, and status every second
        self.update_timer = new_timer(1000, self.monitor)
        self.monitor()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.temperature_label = Label()
        self.setpoint_label = Label()

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
        self.instruments.oven.connectionChanged.connect(
            lambda connected: self.handle_disconnect() if not connected else None
        )
        self.temperatureRead.connect(
            lambda temperature: self.temperature_label.setText(str(temperature))
        )
        self.setpointRead.connect(lambda setpoint: self.setpoint_label.setText(str(setpoint)))

    def handle_disconnect(self):
        null_text = "-----"
        for label in (self.temperature_label, self.setpoint_label):
            label.setText(null_text)

    def monitor(self):
        temperature = self.instruments.oven.read_temp()
        if temperature is not None:
            self.temperatureRead.emit(temperature)

        setpoint = self.instruments.oven.get_setpoint()
        if setpoint is not None:
            self.setpointRead.emit(setpoint)
