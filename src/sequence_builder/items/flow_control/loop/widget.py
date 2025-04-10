from ...base.widget import BaseWidget
from .process import LoopProcess
from PyQt6.QtWidgets import QHBoxLayout, QLabel


class LoopWidget(BaseWidget):
    PROCESS_TYPE = LoopProcess
    SUPPORTS_SUBITEMS = True

    DISPLAY_NAME_PREFIX = "Loop"

    def __init__(self):
        # TODO: implement
        layout = QHBoxLayout()
        super().__init__(layout, self.DISPLAY_NAME_PREFIX)
        self.parameter_widget().layout().addWidget(QLabel("TODO"))

    @classmethod
    def from_dict(cls, data_as_dict):
        # TODO: implement
        return cls()

    def to_dict(self):
        # TODO: implement
        return dict()
