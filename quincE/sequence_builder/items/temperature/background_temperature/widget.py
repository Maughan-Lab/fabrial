from typing import Any, Self

from PyQt6.QtWidgets import QFormLayout

from .....classes import DescriptionInfo
from .....constants.paths.process import filenames
from .....custom_widgets import SpinBox
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import BackgroundTemperatureProcess


class BackgroundTemperatureWidget(AbstractBaseWidget):
    """Enable background temperature monitoring."""

    DISPLAY_NAME_PREFIX = "Enable Background Temperature Monitoring"

    def __init__(self):
        layout = QFormLayout()
        self.interval_spinbox = SpinBox(50)
        AbstractBaseWidget.__init__(
            self,
            layout,
            self.DISPLAY_NAME_PREFIX,
            BackgroundTemperatureProcess,
            "system-monitor.png",
            DescriptionInfo(
                "temperature",
                "background_temperature",
                BackgroundTemperatureProcess.directory_name(),
                DescriptionInfo.Substitutions(
                    parameters_dict={
                        "MEASUREMENT_INTERVAL": encoding.MEASUREMENT_INTERVAL,
                        "MINIMUM_INTERVAL": str(self.interval_spinbox.minimum()),
                    },
                    data_recording_dict={"TEMPERATURE_FILE": filenames.TEMPERATURES},
                ),
            ),
        )
        layout.addRow(encoding.MEASUREMENT_INTERVAL, self.interval_spinbox)

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.interval_spinbox.setValue(data_as_dict[encoding.MEASUREMENT_INTERVAL])
        return widget

    def to_dict(self) -> dict[str, Any]:
        return {encoding.MEASUREMENT_INTERVAL: self.interval_spinbox.value()}
