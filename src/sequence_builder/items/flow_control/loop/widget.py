from ...base_widget import BaseWidget
from .process import LoopProcess
from PyQt6.QtWidgets import QHBoxLayout, QLabel
from typing import Any


class LoopWidget(BaseWidget):
    PROCESS_TYPE = LoopProcess
    SUPPORTS_SUBITEMS = True
    ICON = "arrow-repeat.png"

    DISPLAY_NAME_PREFIX = "Loop"

    def __init__(self):
        # TODO: implement
        layout = QHBoxLayout()
        super().__init__(layout, self.DISPLAY_NAME_PREFIX)
        self.parameter_widget().layout().addWidget(QLabel("TODO"))  # type: ignore

    @classmethod
    def from_dict(cls, data_as_dict: dict[str, Any]):
        # TODO: implement
        return cls()

    def to_dict(self) -> dict[str, Any]:
        # TODO: implement
        return dict()
