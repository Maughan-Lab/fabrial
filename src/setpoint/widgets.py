from PyQt6.QtWidgets import QVBoxLayout, QPushButton
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet  # ../instruments.py
from utility.layouts import add_to_layout  # ../utility


class SetpointWidget(GroupBox):
    """Widget for changing the setpoint."""

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Setpoint", QVBoxLayout, instruments)

        self.create_widgets()
        self.connect_widgets()
        self.connect_signals()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.setpoint_spinbox = TemperatureSpinBox()
        self.button = QPushButton("Change Setpoint")
        add_to_layout(layout, Label("Setpoint"), self.setpoint_spinbox, self.button)

    def connect_widgets(self):
        """Connect internal widget signals."""
        self.button.pressed.connect(self.change_setpoint)
        # trigger the command when Enter is pressed
        self.setpoint_spinbox.connect_to_button(self.button)

    def connect_signals(self):
        """Connect external signals."""
        # oven connection
        self.instruments.oven.connectionChanged.connect(
            lambda connected: self.update_button_states(
                connected, self.instruments.oven.is_unlocked()
            )
        )
        # oven lock
        self.instruments.oven.lockChanged.connect(
            lambda unlocked: self.update_button_states(
                self.instruments.oven.is_connected(), unlocked
            )
        )

    def update_button_states(self, connected: bool, unlocked: bool):
        """Update the states of buttons."""
        # enable the button if the oven is connected and unlocked
        self.button.setEnabled(connected and unlocked)

    def change_setpoint(self):
        """Change the oven's setpoint."""
        self.instruments.oven.acquire()
        self.instruments.oven.change_setpoint(self.setpoint_spinbox.value())
        self.instruments.oven.release()
