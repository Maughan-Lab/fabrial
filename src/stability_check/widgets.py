from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import pyqtSignal
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet, ConnectionStatus  # ../instruments.py
from helper_functions.layouts import (
    add_sublayout,
    add_to_layout,
    add_to_layout_grid,
)  # ../helper_functions
from enums.status import StabilityStatus, STABILITY_TEXT_KEY, STABILITY_COLOR_KEY  # ../enums


class StabilityCheckWidget(GroupBox):
    """Widget for checking whether the temperature is stable."""

    # signals
    stabilityChanged = pyqtSignal(StabilityStatus)
    statusChanged = pyqtSignal(bool)
    cancelSequence = pyqtSignal()

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Temperature Stability Check", QVBoxLayout, instruments)

        self.create_widgets()
        self.connect_widgets()
        self.connect_signals()

        # variables
        # TODO: replace this with checking to see if any StabilityCheckThreads exist
        self.running = False

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.stability_check_button = QPushButton("Check Stability")
        self.detect_setpoint_button = QPushButton("Detect Setpoint")
        self.setpoint_spinbox = TemperatureSpinBox()
        # layout for the label, detect_setpoint_button, and setpoint_spinbox
        inner_layout = add_sublayout(layout, QGridLayout)
        add_to_layout_grid(
            inner_layout,
            (Label("Setpoint"), 0, 0),
            (self.setpoint_spinbox, 1, 0),
            (self.detect_setpoint_button, 1, 1),
        )

        layout.addWidget(self.stability_check_button)

        stability_layout = add_sublayout(layout, QHBoxLayout, QSizePolicy.Policy.Fixed)
        self.stability_label = Label(STABILITY_TEXT_KEY[StabilityStatus.NULL])
        add_to_layout(stability_layout, Label("Stability Status:"), self.stability_label)

    def connect_widgets(self):
        """Connect internal widget signals."""
        # self.stability_check_button.pressed.connect()  # TODO: connect this
        self.detect_setpoint_button.pressed.connect(self.detect_setpoint)

    def connect_signals(self):
        """Connect external signals."""
        # stabilityChanged
        self.stabilityChanged.connect(self.handle_stability_change)
        # statusChanged
        self.statusChanged.connect(
            lambda running: self.update_button_states(
                self.instruments.oven.connection_status == ConnectionStatus.CONNECTED,
                self.instruments.oven.unlocked,
                running,
            )
        )
        # oven connection
        self.instruments.oven.connectionChanged.connect(
            lambda connected: self.update_button_states(
                connected, self.instruments.oven.unlocked, self.running
            )
        )
        # oven lock
        self.instruments.oven.lockChanged.connect(
            lambda unlocked: self.update_button_states(
                self.instruments.oven.connection_status == ConnectionStatus.CONNECTED,
                unlocked,
                self.running,
            )
        )
        # TODO: add and connect a signal for the stability status, like in the SequenceWidget

    def handle_stability_change(self, status: StabilityStatus):
        self.stability_label.setText(STABILITY_TEXT_KEY[status])
        self.stability_label.setStyleSheet("color: " + STABILITY_COLOR_KEY[status])

    def update_button_states(self, connected: bool, unlocked: bool, running: bool):
        """Update the states of buttons."""
        # enable the button if the oven is connected and a check isn't running
        self.detect_setpoint_button.setEnabled(connected and not running)
        # enable the button if the oven is connected and unlocked, and a check isn't running
        self.stability_check_button.setEnabled(connected and unlocked and not running)

    def detect_setpoint(self):
        """
        Attempt to autofill the setpoint box with the oven's current setpoint.
        """
        setpoint = self.instruments.oven.get_setpoint()
        if setpoint is not None:
            self.setpoint_spinbox.setValue(setpoint)
        else:
            self.setpoint_spinbox.clear()  # clear the spinbox if the oven is disconnected
