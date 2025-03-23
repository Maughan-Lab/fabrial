from PyQt6.QtWidgets import QVBoxLayout
from utility.layouts import add_to_layout
from custom_widgets.container import Container
from custom_widgets.label import Label
from . import Encoding


class TestWidget(Container):
    def __init__(self) -> None:
        """Test widget"""
        super().__init__(QVBoxLayout)
        layout: QVBoxLayout = self.layout()  # type: ignore
        self.cry_count_label = Label("")
        self.average_cries_label = Label("")
        add_to_layout(layout, self.cry_count_label, self.average_cries_label)
        self.display_name: str
        print("f")

    @classmethod
    def from_dict(cls: type["TestWidget"], data_as_dict: dict) -> "TestWidget":
        widget = cls()
        widget.display_name = data_as_dict[Encoding.TestWidget.DISPLAY_NAME]
        widget.cry_count_label.setText(str(data_as_dict[Encoding.TestWidget.CRY_COUNT]))
        widget.average_cries_label.setText(str(data_as_dict[Encoding.TestWidget.AVERAGE_CRIES]))
        return widget

    def to_dict(self) -> dict:
        data = {
            Encoding.TestWidget.DISPLAY_NAME: self.display_name,
            Encoding.TestWidget.CRY_COUNT: int(self.cry_count_label.text()),
            Encoding.TestWidget.AVERAGE_CRIES: float(self.average_cries_label.text()),
        }
        return data
