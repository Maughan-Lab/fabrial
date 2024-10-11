from PyQt6.QtWidgets import QGroupBox, QGridLayout
from PyQt6.QtCore import Qt
from custom_widgets.label import Label  # ../custom_widgets
from instruments import InstrumentSet, Status  # ../instruments.py
from helper_functions.new_timer import new_timer  # ../helper_functions


class PassiveMonitoringWidget(QGroupBox):
    """
    Widget for monitoring the oven.

    :param instruments: Container for instruments.
    """

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Measurements")
        # manage the layout
        layout = QGridLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.update()

        # timer to update the oven temperature, setpoint, and status every second
        self.update_timer = new_timer(1000, self.update)

        self.setFixedSize(self.sizeHint())  # make sure expanding the window behaves correctly

    def create_widgets(self, layout: QGridLayout):
        """Create subwidgets."""
        self.temperature_label = Label()
        self.setpoint_label = Label()
        self.status_label = Label()
        # oven temperature
        self.add_widget_row(layout, "Temperature", 0, self.temperature_label)
        # oven setpoint
        self.add_widget_row(layout, "Setpoint", 1, self.setpoint_label)
        # oven stability status
        self.add_widget_row(layout, "Status", 2, self.status_label)

    def add_widget_row(self, layout: QGridLayout, text: str, row: int, label_widget: Label):
        layout.addWidget(Label("Oven " + text + ":"), row, 0, Qt.AlignmentFlag.AlignRight)
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
