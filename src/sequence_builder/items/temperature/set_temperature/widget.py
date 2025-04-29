from ...base_widget import BaseWidget
from .....custom_widgets.spin_box import TemperatureSpinBox
from .....instruments import INSTRUMENTS
from .process import SetTemperatureProcess
from . import encoding
from PyQt6.QtWidgets import QFormLayout
from typing import Any, Self
from ..... import Files


class SetTemperatureWidget(BaseWidget):
    """Set the oven's temperature and wait for it to stabilize."""

    PROCESS_TYPE: type[SetTemperatureProcess] = SetTemperatureProcess
    ICON = "thermometer--arrow.png"

    DISPLAY_NAME_PREFIX = "Set Oven Temperature"

    def __init__(self):
        layout = QFormLayout()
        super().__init__(layout, self.DISPLAY_NAME_PREFIX)
        self.set_description_from_file(
            "temperature",
            "set_temperature.md",
            {
                "MEASUREMENT_INTERVAL": str(self.PROCESS_TYPE.MEASUREMENT_INTERVAL),
                "DIRECTORY_NAME": self.PROCESS_TYPE.DIRECTORY,
                "TEMPERATURE_FILE": encoding.Filenames.TEMPERATURES,
                "METADATA_FILE": Files.Process.Filenames.METADATA,
            },
        )

        self.temperature_spinbox = TemperatureSpinBox(INSTRUMENTS.oven)
        self.temperature_spinbox.textChanged.connect(
            lambda value_as_str: self.setWindowTitle(
                f"{self.DISPLAY_NAME_PREFIX} ({value_as_str} degrees)"
            )
        )
        layout.addRow("Setpoint", self.temperature_spinbox)

    def to_dict(self) -> dict[str, Any]:
        return {encoding.SETPOINT: self.temperature_spinbox.value()}

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.temperature_spinbox.setValue(data_as_dict[encoding.SETPOINT])
        return widget
