from typing import Any, Self

from PyQt6.QtWidgets import QFormLayout

from .....classes import DescriptionInfo
from .....constants.paths.process import filenames
from .....custom_widgets import DoubleSpinBox
from .....instruments import INSTRUMENTS
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import IncrementTemperatureProcess


class IncrementTemperatureWidget(AbstractBaseWidget):
    """Increment the oven's temperature and wait for it to stabilize."""

    DISPLAY_NAME_PREFIX = "Increment Oven Temperature"

    def __init__(self):
        layout = QFormLayout()
        AbstractBaseWidget.__init__(
            self,
            layout,
            self.DISPLAY_NAME_PREFIX,
            IncrementTemperatureProcess,
            "thermometer--plus.png",
            DescriptionInfo(
                "temperature",
                "increment_temperature",
                IncrementTemperatureProcess.directory_name(),
                DescriptionInfo.Substitutions(
                    overview_dict={
                        "MEASUREMENT_INTERVAL": str(
                            IncrementTemperatureProcess.MEASUREMENT_INTERVAL
                        )
                    },
                    parameters_dict={"INCREMENT": encoding.INCREMENT},
                    data_recording_dict={
                        "TEMPERATURE_FILE": filenames.TEMPERATURES,
                        "GRAPH_FILE": IncrementTemperatureProcess.GRAPH_FILENAME,
                    },
                ),
            ),
        )

        oven = INSTRUMENTS.oven
        maximum_temperature = oven.maximum_temperature()
        self.increment_spinbox = DoubleSpinBox(
            oven.num_decimals(), -maximum_temperature, maximum_temperature
        )
        self.increment_spinbox.textChanged.connect(
            lambda value_as_str: self.setWindowTitle(
                f"{self.DISPLAY_NAME_PREFIX} ({value_as_str} degrees)"
            )
        )
        layout.addRow(encoding.INCREMENT, self.increment_spinbox)

    def to_dict(self) -> dict[str, Any]:
        return {encoding.INCREMENT: self.increment_spinbox.value()}

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.increment_spinbox.setValue(data_as_dict[encoding.INCREMENT])
        return widget
