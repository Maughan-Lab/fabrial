from PyQt6.QtWidgets import QTabWidget, QWidget

from ..utility.images import make_icon
from .oven_control import OvenControlTab
from .sequence_builder import SequenceBuilderTab
from .sequence_display import SequenceDisplayTab


class TabWidget(QTabWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.sequence_visuals_tab = SequenceDisplayTab()
        self.sequence_builder_tab = SequenceBuilderTab(self.sequence_visuals_tab)
        self.oven_control_tab = OvenControlTab()

        self.addTab(
            self.sequence_builder_tab,
            make_icon(self.sequence_builder_tab.ICON_FILE),
            "Sequence Builder",
        )
        self.addTab(self.sequence_visuals_tab, make_icon("chart.png"), "Sequence Visuals")
        self.addTab(
            self.oven_control_tab, make_icon(self.oven_control_tab.ICON_FILE), "Oven Control"
        )

        self.currentChanged.connect(lambda index: self.widget(index).setFocus())  # type: ignore
