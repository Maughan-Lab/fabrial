from pathlib import Path

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QFormLayout

from quincy.custom_widgets import SpinBox
from quincy.sequence_builder import ItemWidget
from quincy.utility import layout as layout_util
from quincy.utility.descriptions import TextDescription

BASE_DISPLAY_NAME = "Hold"
HOURS_LABEL = "Hours"
MINUTES_LABEL = "Minutes"
SECONDS_LABEL = "Seconds"


class HoldWidget(ItemWidget):
    """Hold for a duration; widget."""

    def __init__(self, hours: int, minutes: int, seconds: int):
        layout = QFormLayout()

        ItemWidget.__init__(
            self,
            layout,
            BASE_DISPLAY_NAME,
            QIcon(str(Path(__file__).parent.joinpath("clock-select.png"))),
            TextDescription(
                "Hold",
                "Hold for the provided duration.",
                {
                    HOURS_LABEL: "The number of hours to hold for.",
                    MINUTES_LABEL: "The number of minutes to hold for.",
                    SECONDS_LABEL: "The number of seconds to hold for.",
                },
            ),
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
        self.setWindowTitle(
            f"{BASE_DISPLAY_NAME} ({self.hours_spinbox.text()} hours, "
            f"{self.minutes_spinbox.text()} minutes, {self.seconds_spinbox.text()} seconds)"
        )
