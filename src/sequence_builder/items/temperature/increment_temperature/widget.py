from typing import Any, Self

from PyQt6.QtWidgets import QFormLayout

from ..... import Files
from .....classes.descriptions import DescriptionInfo
from .....custom_widgets.spin_box import DoubleSpinBox
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import IncrementTemperatureProcess


class IncrementTemperatureWidget(AbstractBaseWidget):
    """Increment the oven's temperature and wait for it to stabilize."""

    DISPLAY_NAME_PREFIX = "Increment Oven Temperature"

    def __init__(self):
        layout = QFormLayout()
        super().__init__(
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
                    data_recording_dict={"TEMPERATURE_FILE": Files.Process.Filenames.TEMPERATURES},
                ),
            ),
        )

        self.increment_spinbox = DoubleSpinBox(1)
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
