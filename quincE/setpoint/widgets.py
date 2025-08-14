from PyQt6.QtWidgets import QPushButton, QVBoxLayout

from ..custom_widgets import GroupBox, Label, OkDialog, TemperatureSpinBox
from ..instruments import INSTRUMENTS
from ..utility import layout as layout_util


class SetpointWidget(GroupBox):
    """Widget for changing the setpoint."""

    def __init__(self):
        GroupBox.__init__(self, "Setpoint", QVBoxLayout())
        self.oven = INSTRUMENTS.oven

        self.create_widgets()
        self.connect_widgets()
        self.connect_signals()

    def create_widgets(self):
        """Create subwidgets."""
        layout: QVBoxLayout = self.layout()  # type: ignore

        self.setpoint_spinbox = TemperatureSpinBox(self.oven)
        self.button = QPushButton("Change Setpoint")
        layout_util.add_to_layout(layout, Label("Setpoint"), self.setpoint_spinbox, self.button)

    def connect_widgets(self):
        """Connect internal widget signals."""
        self.button.pressed.connect(self.change_setpoint)
        # trigger the command when Enter is pressed
        self.setpoint_spinbox.connect_to_button(self.button)

    def connect_signals(self):
        """Connect external signals."""
        # oven connection
        self.oven.connectionChanged.connect(
            lambda connected: self.update_button_states(connected, self.oven.is_unlocked())
        )
        # oven lock
        self.oven.lockChanged.connect(
            lambda unlocked: self.update_button_states(self.oven.is_connected(), unlocked)
        )

    def update_button_states(self, connected: bool, unlocked: bool):
        """Update the states of buttons."""
        # enable the button if the oven is connected and unlocked
        self.button.setEnabled(connected and unlocked)

    def change_setpoint(self):
        """Change the oven's setpoint."""
        # intentionally not locking the oven because this operation is fast
        success = self.oven.change_setpoint(self.setpoint_spinbox.value())
        if not success:
            # this will probably never run, but it could if the read operation fails
            OkDialog("Error", "Failed to change setpoint, please try again.").exec()
