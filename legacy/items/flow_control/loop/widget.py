from typing import Any

from PyQt6.QtWidgets import QFormLayout

from .....classes import DescriptionInfo
from .....custom_widgets import SpinBox
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import LoopProcess


class LoopWidget(AbstractBaseWidget):
    DISPLAY_NAME_PREFIX = "Loop"

    def __init__(self):
        layout = QFormLayout()
        AbstractBaseWidget.__init__(
            self,
            layout,
            self.DISPLAY_NAME_PREFIX,
            LoopProcess,
            "arrow-repeat.png",
            DescriptionInfo(
                "flow_control",
                "loop",
                LoopProcess.directory_name(),
                DescriptionInfo.Substitutions(
                    parameters_dict={"NUM_LOOPS": encoding.NUMBER_OF_LOOPS}
                ),
            ),
            True,
        )

        self.loop_spinbox = SpinBox()
        self.loop_spinbox.setMinimum(1)
        layout.addRow(encoding.NUMBER_OF_LOOPS, self.loop_spinbox)
        self.loop_spinbox.textChanged.connect(
            lambda value_as_str: self.setWindowTitle(f"{self.DISPLAY_NAME_PREFIX} ({value_as_str})")
        )

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]):
        widget = cls()
        widget.loop_spinbox.setValue(data_as_dict[encoding.NUMBER_OF_LOOPS])
        return widget

    def to_dict(self) -> dict[str, Any]:
        return {encoding.NUMBER_OF_LOOPS: self.loop_spinbox.value()}
