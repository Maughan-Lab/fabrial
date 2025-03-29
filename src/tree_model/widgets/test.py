from .base import BaseWidget
from PyQt6.QtWidgets import QVBoxLayout
from utility.layouts import add_to_layout
from custom_widgets.label import Label
from ..data_encodings import test as DATA


class TestWidget(BaseWidget):
    def __init__(self) -> None:
        """Test widget"""
        super().__init__("Test Widget", QVBoxLayout)

        layout: QVBoxLayout = self.layout()  # type: ignore
        self.cry_count_label = Label("")
        self.average_cries_label = Label("")
        add_to_layout(layout, self.cry_count_label, self.average_cries_label)

    @classmethod
    def from_dict(cls: type["TestWidget"], data_as_dict: dict) -> "TestWidget":
        widget = cls()
        widget.display_name = data_as_dict[DATA.DISPLAY_NAME]
        widget.cry_count_label.setText(str(data_as_dict[DATA.CRY_COUNT]))
        widget.average_cries_label.setText(str(data_as_dict[DATA.AVERAGE_CRIES]))
        return widget

    def to_dict(self) -> dict:
        data = {
            DATA.DISPLAY_NAME: self.display_name,
            DATA.CRY_COUNT: int(self.cry_count_label.text()),
            DATA.AVERAGE_CRIES: float(self.average_cries_label.text()),
        }
        return data
