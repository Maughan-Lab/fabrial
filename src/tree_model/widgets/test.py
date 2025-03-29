from .base import BaseWidget
from PyQt6.QtWidgets import QVBoxLayout
from ...utility.layouts import add_to_layout
from ...custom_widgets.label import Label
from typing import Self
from ..data_encodings import test as DATA
from ..data_encodings.display_name import DISPLAY_NAME


class TestWidget(BaseWidget):
    def __init__(self) -> None:
        """Test widget"""
        super().__init__(QVBoxLayout)

        layout: QVBoxLayout = self.layout()  # type: ignore
        self.cry_count_label = Label("")
        self.average_cries_label = Label("")
        add_to_layout(layout, self.cry_count_label, self.average_cries_label)

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict) -> Self:
        widget = cls()
        widget.set_display_name(data_as_dict[DISPLAY_NAME])
        widget.cry_count_label.setText(str(data_as_dict[DATA.CRY_COUNT]))
        widget.average_cries_label.setText(str(data_as_dict[DATA.AVERAGE_CRIES]))
        return widget

    def to_dict(self) -> dict:
        data = {
            DISPLAY_NAME: self.display_name,
            DATA.CRY_COUNT: int(self.cry_count_label.text()),
            DATA.AVERAGE_CRIES: float(self.average_cries_label.text()),
        }
        return data
