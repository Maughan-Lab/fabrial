from typing import Any, Self

from PyQt6.QtWidgets import QFormLayout

from .....classes import DescriptionInfo
from .....constants.paths.process import filenames
from .....custom_widgets import TemperatureSpinBox
from .....instruments import INSTRUMENTS
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import SetTemperatureProcess


class SetTemperatureWidget(AbstractBaseWidget):
    """Set the oven's temperature and wait for it to stabilize."""

    DISPLAY_NAME_PREFIX = "Set Oven Temperature"

    def __init__(self):
        layout = QFormLayout()
        AbstractBaseWidget.__init__(
            self,
            layout,
            self.DISPLAY_NAME_PREFIX,
            SetTemperatureProcess,
            "thermometer--arrow.png",
            DescriptionInfo(
                "temperature",
                "set_temperature",
                SetTemperatureProcess.directory_name(),
                DescriptionInfo.Substitutions(
                    overview_dict={
                        "MEASUREMENT_INTERVAL": str(SetTemperatureProcess.MEASUREMENT_INTERVAL)
                    },
                    parameters_dict={"SETPOINT": encoding.SETPOINT},
                    data_recording_dict={
                        "TEMPERATURE_FILE": filenames.TEMPERATURES,
                        "GRAPH_FILE": SetTemperatureProcess.GRAPH_FILENAME,
                    },
                ),
            ),
        )

        self.temperature_spinbox = TemperatureSpinBox(INSTRUMENTS.oven)
        self.temperature_spinbox.textChanged.connect(
            lambda value_as_str: self.setWindowTitle(
                f"{self.DISPLAY_NAME_PREFIX} ({value_as_str} degrees)"
            )
        )
        layout.addRow(encoding.SETPOINT, self.temperature_spinbox)

    def to_dict(self) -> dict[str, Any]:
        return {encoding.SETPOINT: self.temperature_spinbox.value()}

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.temperature_spinbox.setValue(data_as_dict[encoding.SETPOINT])
        return widget
