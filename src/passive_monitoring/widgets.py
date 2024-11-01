from PyQt6.QtWidgets import QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet, Status  # ../instruments.py
from helper_functions.new_timer import new_timer  # ../helper_functions


class PassiveMonitoringWidget(GroupBox):
    """Widget for monitoring the oven."""

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Measurements", QGridLayout, instruments)

        self.create_widgets()

        # timer to update the oven temperature, setpoint, and status every second
        self.update_timer = new_timer(1000, self.update)

        self.update()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.temperature_label = Label()
        self.setpoint_label = Label()
        self.status_label = Label()

        self.add_widget_row(layout, "Temperature", 0, self.temperature_label)  # oven temperature
        self.add_widget_row(layout, "Setpoint", 1, self.setpoint_label)  # oven setpoint
        self.add_widget_row(layout, "Status", 2, self.status_label)  # oven stability status

    def add_widget_row(self, layout: QGridLayout, text: str, row: int, label_widget: Label):
        category_label = Label("Oven " + text + ":")

        font = QFont("Arial", 16)
        # category_label.setFont(font)
        label_widget.setFont(font)

        layout.addWidget(category_label, row, 0, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(label_widget, row, 1)

    def update(self):
        """Update the state of dynamic widgets."""
        # temperature
        temperature = self.instruments.oven.read_temp()
        self.temperature_label.setText(str(temperature) if temperature is not None else "-----")
        # setpoint
        setpoint = self.instruments.oven.get_setpoint()
        self.setpoint_label.setText(str(setpoint) if setpoint is not None else "-----")
        # status
        text = ""
        color = ""
        match self.instruments.oven.status:
            case Status.STABLE:
                text = "Stable"
                color = "green"
            case Status.UNSTABLE:
                text = "Unstable"
                color = "red"
            case Status.ERROR:
                text = "Error"
                color = "red"
            case Status.CANCELED:
                text = "Canceled"
                color = "red"
            case Status.CHECKING:
                text = "Checking..."
                color = "orange"
            case _:
                text = "-----------"
                color = "white"
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: " + color)
