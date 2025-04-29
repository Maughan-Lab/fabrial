from ...base_widget import BaseWidget
from .process import LoopProcess
from . import encoding
from PyQt6.QtWidgets import QFormLayout
from .....custom_widgets.spin_box import SpinBox
from typing import Any


class LoopWidget(BaseWidget):
    PROCESS_TYPE = LoopProcess
    SUPPORTS_SUBITEMS = True
    ICON = "arrow-repeat.png"

    DISPLAY_NAME_PREFIX = "Loop"

    def __init__(self):
        layout = QFormLayout()
        super().__init__(layout, self.DISPLAY_NAME_PREFIX)
        self.loop_spinbox = SpinBox()
        self.loop_spinbox.setMinimum(1)
        layout.addRow("Number of Loops", self.loop_spinbox)

        # TODO: implement

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]):
        widget = cls()
        widget.loop_spinbox.setValue(data_as_dict[encoding.NUMBER_OF_LOOPS])
        return widget

    def to_dict(self) -> dict[str, Any]:
        return {encoding.NUMBER_OF_LOOPS: self.loop_spinbox.value()}
