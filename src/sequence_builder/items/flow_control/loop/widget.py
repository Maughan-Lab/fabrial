from ...base_widget import BaseWidget
from .process import LoopProcess
from . import encoding
from PyQt6.QtWidgets import QFormLayout
from .....custom_widgets.spin_box import SpinBox
from typing import Any


class LoopWidget(BaseWidget):
    DISPLAY_NAME_PREFIX = "Loop"

    def __init__(self):
        layout = QFormLayout()
        # TODO: description
        super().__init__(
            layout, self.DISPLAY_NAME_PREFIX, LoopProcess, "arrow-repeat.png", None, True
        )

        self.loop_spinbox = SpinBox()
        self.loop_spinbox.setMinimum(1)
        layout.addRow("Number of Loops", self.loop_spinbox)
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
