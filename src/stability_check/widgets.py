from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QPushButton
from PyQt6.QtCore import pyqtSignal, QThreadPool
from ..custom_widgets.spin_box import TemperatureSpinBox
from ..custom_widgets.label import Label
from ..custom_widgets.groupbox import GroupBox
from ..custom_widgets.dialog import OkDialog
from ..custom_widgets.progressbar import ProgressBar
from ..instruments import INSTRUMENTS
from ..utility.layouts import add_sublayout, add_to_layout
from ..enums.status import StabilityStatus
from .stability_check import StabilityCheckThread
from typing import Type


class StabilityCheckWidget(GroupBox):
    """Widget for checking whether the temperature is stable."""

    # signals
    statusChanged = pyqtSignal(bool)
    cancelStabilityCheck = pyqtSignal()

    def __init__(self, thread_type: Type[StabilityCheckThread] = StabilityCheckThread):
        """
        :param thread_type: The type of thread object to use when running stability checks.
        """
        super().__init__("Temperature Stability Check", QVBoxLayout())

        self.thread_type = thread_type

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
        self.stability_label = Label(StabilityStatus.NULL.status_text)
        self.progressbar = ProgressBar(0, self.thread_type.MINIMUM_MEASUREMENTS)
        # layout for the label, detect_setpoint_button, and setpoint_spinbox
        inner_layout = add_sublayout(layout, QGridLayout)
        inner_layout.addWidget(Label("Setpoint"), 0, 0)
        inner_layout.addWidget(self.setpoint_spinbox, 1, 0)
        inner_layout.addWidget(self.detect_setpoint_button, 1, 1)

        add_to_layout(layout, self.stability_check_button, self.progressbar)

        stability_layout = add_sublayout(layout, QHBoxLayout)
        add_to_layout(stability_layout, Label("Stability Status:"), self.stability_label)

    def connect_widgets(self):
        """Connect internal widget signals."""
        self.setpoint_spinbox.connect_to_button(self.stability_check_button)
        self.stability_check_button.pressed.connect(self.start_stability_check)
        self.detect_setpoint_button.pressed.connect(self.detect_setpoint)

    def connect_signals(self):
        """Connect external signals."""
        INSTRUMENTS.oven.connectionChanged.connect(self.handle_connection_change)
        INSTRUMENTS.oven.lockChanged.connect(self.handle_lock_change)

    def handle_stability_change(self, status: StabilityStatus):
        """Handle a stability change."""
        self.stability_label.setText(status.status_text)
        self.stability_label.setStyleSheet("color: " + status.color)

    def handle_status_change(self, running: bool):
        """Handle a status change."""
        self.update_button_states(
            INSTRUMENTS.oven.is_connected(), INSTRUMENTS.oven.is_unlocked(), running
        )
        if not running:
            self.progressbar.setValue(self.progressbar.maximum())
        self.statusChanged.emit(running)

    def handle_connection_change(self, connected: bool):
        """Handle the oven's connectionChanged signal."""
        self.update_button_states(connected, INSTRUMENTS.oven.is_unlocked(), self.is_running())

    def handle_lock_change(self, unlocked: bool):
        """Handle the oven's lockChanged signal."""
        self.update_button_states(INSTRUMENTS.oven.is_connected(), unlocked, self.is_running())
        if not self.is_running() and not unlocked:
            self.reset()

    def reset(self):
        """Reset the stability label and setpoint spinbox."""
        self.handle_stability_change(StabilityStatus.NULL)
        self.setpoint_spinbox.setValue(0.0)
        self.progressbar.reset()

    def update_button_states(self, connected: bool, unlocked: bool, running: bool):
        """Update the states of buttons."""
        # enable the buttons if the oven is connected and unlocked, and a check isn't running
        enabled = connected and unlocked and not running
        self.detect_setpoint_button.setEnabled(enabled)
        self.stability_check_button.setEnabled(enabled)

    def detect_setpoint(self):
        """Attempt to autofill the setpoint box with the oven's current setpoint."""
        setpoint = INSTRUMENTS.oven.get_setpoint()
        if setpoint is not None:
            self.setpoint_spinbox.setValue(setpoint)
        else:
            self.setpoint_spinbox.setValue(0.0)  # clear the spinbox if the oven is disconnected

    # ----------------------------------------------------------------------------------------------
    # stability check
    def start_stability_check(self):
        if not self.is_running():
            self.progressbar.setValue(0)

            thread = self.thread_type(INSTRUMENTS, self.setpoint_spinbox.value())
            thread.signals.statusChanged.connect(self.handle_status_change)
            thread.signals.stabilityChanged.connect(self.handle_stability_change)
            thread.signals.progressed.connect(self.progressbar.increment)
            self.cancelStabilityCheck.connect(thread.cancel_stability_check)

            self.threadpool.start(thread)

        else:
            # this should never run
            OkDialog(
                "Error!", "A stability check is already running. This is a bug, please report it."
            ).exec()

    def is_running(self) -> bool:
        """Determine if a StabilityCheckThread is active."""
        return self.threadpool.activeThreadCount() != 0
