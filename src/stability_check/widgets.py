from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton, QSizePolicy
from PyQt6.QtCore import pyqtSignal, QThreadPool
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from custom_widgets.dialog import OkDialog
from instruments import InstrumentSet  # ../instruments.py
from utility.layouts import (
    add_sublayout,
    add_to_layout,
    add_to_layout_grid,
)  # ../utility
from enums.status import StabilityStatus  # ../enums
from .stability_check import StabilityCheckThread


class StabilityCheckWidget(GroupBox):
    """Widget for checking whether the temperature is stable."""

    # signals
    statusChanged = pyqtSignal(bool)
    cancelStabilityCheck = pyqtSignal()

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Temperature Stability Check", QVBoxLayout, instruments)

        self.create_widgets()
        self.connect_widgets()
        self.connect_signals()

        self.threadpool = QThreadPool()

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
        self.stability_label = Label(str(StabilityStatus.NULL))
        add_to_layout(stability_layout, Label("Stability Status:"), self.stability_label)

    def connect_widgets(self):
        """Connect internal widget signals."""
        self.setpoint_spinbox.connect_to_button(self.stability_check_button)
        self.stability_check_button.pressed.connect(self.start_stability_check)
        self.detect_setpoint_button.pressed.connect(self.detect_setpoint)

    def connect_signals(self):
        """Connect external signals."""
        # statusChanged
        self.statusChanged.connect(
            lambda running: self.update_button_states(
                self.instruments.oven.is_connected(),
                self.instruments.oven.is_unlocked(),
                running,
            )
        )
        # oven connection
        self.instruments.oven.connectionChanged.connect(
            lambda connected: self.update_button_states(
                connected, self.instruments.oven.is_unlocked(), self.is_running()
            )
        )
        # oven lock
        self.instruments.oven.lockChanged.connect(
            lambda unlocked: self.update_button_states(
                self.instruments.oven.is_connected(),
                unlocked,
                self.is_running(),
            )
        )

    def handle_stability_change(self, status: StabilityStatus):
        self.stability_label.setText(str(status))
        self.stability_label.setStyleSheet("color: " + status.to_color())

    def reset(self):
        """Reset the stability label and setpoint spinbox."""
        self.handle_stability_change(StabilityStatus.NULL)
        self.setpoint_spinbox.setValue(0.0)

    def update_button_states(self, connected: bool, unlocked: bool, running: bool):
        """Update the states of buttons."""
        # enable the button if the oven is connected and a check isn't running
        self.detect_setpoint_button.setEnabled(connected and not running)
        # enable the button if the oven is connected and unlocked, and a check isn't running
        self.stability_check_button.setEnabled(connected and unlocked and not running)

    def detect_setpoint(self):
        """Attempt to autofill the setpoint box with the oven's current setpoint."""
        setpoint = self.instruments.oven.get_setpoint()
        if setpoint is not None:
            self.setpoint_spinbox.setValue(setpoint)
        else:
            self.setpoint_spinbox.setValue(0.0)  # clear the spinbox if the oven is disconnected

    # ----------------------------------------------------------------------------------------------
    # stability check
    def start_stability_check(self):
        if not self.is_running():
            thread = self.new_thread()
            thread.statusChanged.connect(self.statusChanged.emit)
            thread.stabilityChanged.connect(self.handle_stability_change)
            self.cancelStabilityCheck.connect(thread.cancel_stability_check)

            self.threadpool.start(thread)

        else:
            # this should never run
            OkDialog(
                "Error!", "A stability check is already running. This is a bug, please report it."
            ).exec()

    def new_thread(self):  # this is necessary for testing
        """Create a new StabilityCheckThread."""
        return StabilityCheckThread(self.instruments, self.setpoint_spinbox.value())

    def is_running(self) -> bool:
        """Determine if a StabilityCheckThread is active."""
        return self.threadpool.activeThreadCount() != 0
