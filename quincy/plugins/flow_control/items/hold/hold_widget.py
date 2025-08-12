from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFormLayout

from quincy.custom_widgets import Container, SpinBox
from quincy.sequence_builder import ItemWidget
from quincy.utility import layout as layout_util
from quincy.utility.descriptions import DescriptionInfo, Substitutions

BASE_DISPLAY_NAME = "Hold"


class HoldWidget(ItemWidget):
    """Hold for a duration; widget."""

    def __init__(self, hours: int, minutes: int, seconds: int):
        layout = QFormLayout()
        parameter_widget = Container(layout)

        ItemWidget.__init__(
            self,
            parameter_widget,
            BASE_DISPLAY_NAME,
            QIcon(str(Path(__file__).parent.joinpath("clock-select.png"))),
            None,
        )

        self.hours_spinbox = SpinBox(initial_value=hours)
        self.minutes_spinbox = SpinBox(initial_value=minutes)
        self.seconds_spinbox = SpinBox(initial_value=seconds)
        layout_util.add_to_form_layout(
            layout,
            ("Hours", self.hours_spinbox),
            ("Minutes", self.minutes_spinbox),
            ("Seconds", self.seconds_spinbox),
        )

        for spinbox in [self.hours_spinbox, self.minutes_spinbox, self.seconds_spinbox]:
            spinbox.editingFinished.connect(self.handle_value_change)

        if (hours, minutes, seconds) != (0, 0, 0):
            self.handle_value_change()  # start with the correct title

    def handle_value_change(self):
        """Handle any of the duration spinboxes changing."""
        hours = self.hours_spinbox.text()
        minutes = self.minutes_spinbox.text()
        seconds = self.seconds_spinbox.text()
        self.setWindowTitle(
            f"{BASE_DISPLAY_NAME} ({hours} hours, {minutes} minutes, {seconds} seconds)"
        )
