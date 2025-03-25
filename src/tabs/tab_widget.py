from PyQt6.QtWidgets import QTabWidget, QWidget
from .oven_control import OvenControlTab
from instruments import InstrumentSet


class TabWidget(QTabWidget):
    def __init__(self, parent: QWidget | None, instruments: InstrumentSet):
        super().__init__(parent)
        self.setDocumentMode(True)
        self.oven_control_tab = OvenControlTab(instruments)
        self.test_tab = QWidget()
        # TODO: figure out how to add a horizontal separator to make this look better

        self.addTab(self.oven_control_tab, "Oven Control")
        self.addTab(self.test_tab, "Test Tab")
