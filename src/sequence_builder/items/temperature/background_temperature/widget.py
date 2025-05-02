from typing import Any, Self

from PyQt6.QtWidgets import QFormLayout

from ..... import Files
from .....classes.descriptions import DescriptionInfo
from .....custom_widgets.spin_box import SpinBox
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import BackgroundTemperatureProcess


class BackgroundTemperatureWidget(AbstractBaseWidget):
    """Enable background temperature monitoring."""

    DISPLAY_NAME_PREFIX = "Enable Background Temperature Monitoring"

    def __init__(self):
        layout = QFormLayout()
        self.interval_spinbox = SpinBox(50)
        super().__init__(
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
                        "MINIMUM_INTERVAL": self.interval_spinbox.minimum(),
                    },
                    data_recording_dict={"TEMPERATURE_FILE": Files.Process.Filenames.TEMPERATURES},
                ),
            ),
        )
        layout.addRow(encoding.MEASUREMENT_INTERVAL, self.interval_spinbox)

        self.interval_spinbox.textChanged.connect(
            lambda value_as_str: self.setWindowTitle(
                f"{self.DISPLAY_NAME_PREFIX} ({value_as_str} ms)"
            )
        )

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.interval_spinbox.setValue(data_as_dict[encoding.MEASUREMENT_INTERVAL])
        return widget

    def to_dict(self) -> dict[str, Any]:
        return {encoding.MEASUREMENT_INTERVAL: self.interval_spinbox.value()}
