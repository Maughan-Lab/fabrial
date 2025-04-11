from PyQt6.QtWidgets import QTabWidget, QWidget
from .oven_control import OvenControlTab
from .sequence_builder import SequenceBuilderTab
from .sequence_display import SequenceDisplayTab
from ..instruments import InstrumentSet


class TabWidget(QTabWidget):
    def __init__(self, parent: QWidget | None, instruments: InstrumentSet):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.oven_control_tab = OvenControlTab(instruments)
        self.addTab(self.oven_control_tab, "Oven Control")

        self.sequence_builder_tab = SequenceBuilderTab(instruments)
        self.addTab(self.sequence_builder_tab, "Sequence Builder")

        self.sequence_visuals_tab = SequenceDisplayTab()
        self.addTab(self.sequence_visuals_tab, "Sequence Visuals")
