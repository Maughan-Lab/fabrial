from PyQt6.QtWidgets import QVBoxLayout, QWidget
from ..custom_widgets.widget import Widget
from ..utility.layouts import clear_layout


class SequenceDisplayTab(Widget):
    """
    Tab for displaying widgets from the sequence runtime. This should only ever hold one widget at a
    time.
    """

    def __init__(self):
        super().__init__(QVBoxLayout())

    def set_central_widget(self, widget: QWidget):
        """Set the central widget."""
        layout: QVBoxLayout = self.layout()  # type: ignore
        clear_layout(layout)
        layout.addWidget(widget)
