from typing import Any, Self

from PyQt6.QtWidgets import QFormLayout

from .....classes import DescriptionInfo
from .....custom_widgets import SpinBox
from .....utility import layout as layout_util
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import HoldProcess


class HoldWidget(AbstractBaseWidget):
    """Hold for a duration."""

    BASE_DISPLAY_NAME = "Hold"

    def __init__(self):
        layout = QFormLayout()
        AbstractBaseWidget.__init__(
            self,
            layout,
            self.BASE_DISPLAY_NAME,
            HoldProcess,
            "clock-select.png",
            DescriptionInfo(
                "flow_control",
                "hold",
                HoldProcess.directory_name(),
                DescriptionInfo.Substitutions(
                    parameters_dict={
                        "HOURS": encoding.HOURS,
                        "MINUTES": encoding.MINUTES,
                        "SECONDS": encoding.SECONDS,
                    }
                ),
            ),
        )

        self.hours_spinbox = SpinBox()
        self.minutes_spinbox = SpinBox()
        self.seconds_spinbox = SpinBox()
        self.spinboxes = (self.hours_spinbox, self.minutes_spinbox, self.seconds_spinbox)
        layout_util.add_to_form_layout(
            layout,
            (encoding.HOURS, self.hours_spinbox),
            (encoding.MINUTES, self.minutes_spinbox),
            (encoding.SECONDS, self.seconds_spinbox),
        )

        for spinbox in self.spinboxes:
            spinbox.textChanged.connect(self.handle_value_change)

    def handle_value_change(self, *args):
        """Handle any of the duration spinboxes changing."""
        hours = self.hours_spinbox.text()
        minutes = self.minutes_spinbox.text()
        seconds = self.seconds_spinbox.text()
        self.setWindowTitle(
            f"{self.BASE_DISPLAY_NAME} ({hours} hours, {minutes} minutes, {seconds} seconds)"
        )

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.hours_spinbox.setValue(data_as_dict[encoding.HOURS])
        widget.minutes_spinbox.setValue(data_as_dict[encoding.MINUTES])
        widget.seconds_spinbox.setValue(data_as_dict[encoding.SECONDS])
        return widget

    def to_dict(self) -> dict[str, Any]:
        return {
            encoding.HOURS: self.hours_spinbox.value(),
            encoding.MINUTES: self.minutes_spinbox.value(),
            encoding.SECONDS: self.seconds_spinbox.value(),
        }
