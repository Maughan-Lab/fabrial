from ...base_widget import AbstractBaseWidget
from ..set_temperature.encoding import Filenames
from .....custom_widgets.spin_box import DoubleSpinBox
from .process import IncrementTemperatureProcess
from . import encoding
from PyQt6.QtWidgets import QFormLayout
from typing import Any, Self
from ..... import Files
from .....classes.descriptions import DescriptionInfo


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
                DescriptionInfo.Substitutions(
                    overview_dict={
                        "MEASUREMENT_INTERVAL": str(
                            IncrementTemperatureProcess.MEASUREMENT_INTERVAL
                        )
                    },
                    parameters_dict={"INCREMENT": encoding.INCREMENT},
                    data_recording_dict={
                        "DIRECTORY_NAME": IncrementTemperatureProcess.directory_name(),
                        "TEMPERATURE_FILE": Filenames.TEMPERATURES,
                        "METADATA_FILE": Files.Process.Filenames.METADATA,
                    },
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
