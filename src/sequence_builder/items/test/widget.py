from ..base.widget import BaseWidget
from .process import TestProcess
from PyQt6.QtWidgets import QVBoxLayout
from ....utility.layouts import add_to_layout
from ....custom_widgets.label import Label
from typing import Self
from . import encoding as DATA


class TestWidget(BaseWidget):
    """Test widget"""

    PROCESS_TYPE = TestProcess

    def __init__(self):
        layout = QVBoxLayout()
        super().__init__(layout, "Test Widget")

        self.cry_count_label = Label("")
        self.average_cries_label = Label("")
        add_to_layout(layout, self.cry_count_label, self.average_cries_label)

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict) -> Self:
        widget = cls()
        widget.cry_count_label.setText(str(data_as_dict[DATA.CRY_COUNT]))
        widget.average_cries_label.setText(str(data_as_dict[DATA.AVERAGE_CRIES]))
        return widget

    def to_dict(self) -> dict:
        data = {
            DATA.CRY_COUNT: int(self.cry_count_label.text()),
            DATA.AVERAGE_CRIES: float(self.average_cries_label.text()),
        }
        return data
