from typing import Any, Self

from PyQt6.QtWidgets import QFormLayout

from .....classes import DescriptionInfo
from .....custom_widgets import TemperatureSpinBox
from .....instruments import INSTRUMENTS
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import SetNoStabilizeProcess


class SetNoStabilizeWidget(AbstractBaseWidget):
    """Set the setpoint without stabilizing."""

    DISPLAY_NAME_PREFIX = "Set Oven Temperature (No Stabilization)"

    def __init__(self):
        layout = QFormLayout()
        AbstractBaseWidget.__init__(
            self,
            layout,
            self.DISPLAY_NAME_PREFIX,
            SetNoStabilizeProcess,
            "thermometer.png",
            DescriptionInfo(
                "temperature",
                "set_no_stabilize",
                SetNoStabilizeProcess.directory_name(),
                DescriptionInfo.Substitutions(parameters_dict={"SETPOINT": encoding.SETPOINT}),
            ),
        )

        self.temperature_spinbox = TemperatureSpinBox(INSTRUMENTS.oven)
        self.temperature_spinbox.textChanged.connect(
            lambda value_as_str: self.setWindowTitle(
                f"{self.DISPLAY_NAME_PREFIX} ({value_as_str} degrees)"
            )
        )
        layout.addRow(encoding.SETPOINT, self.temperature_spinbox)

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.temperature_spinbox.setValue(data_as_dict[encoding.SETPOINT])
        return widget

    def to_dict(self) -> dict[str, Any]:
        return {encoding.SETPOINT: self.temperature_spinbox.value()}
