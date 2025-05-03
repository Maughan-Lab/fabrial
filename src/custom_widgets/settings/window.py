from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QTabWidget

from ... import Files
from ...tabs.oven_control import OvenControlTab
from ...tabs.sequence_builder import SequenceBuilderTab
from ...utility.images import make_icon
from .gamry import GamrySettingsTab
from .oven import OvenSettingsTab
from .sequence import SequenceSettingsTab


class ApplicationSettingsWindow(QTabWidget):
    """Settings window the application's settings."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{Files.APPLICATION_NAME} - Settings")
        self.sequence_tab = SequenceSettingsTab()
        self.oven_tab = OvenSettingsTab()
        self.gamry_tab = GamrySettingsTab()

        self.addTab(self.sequence_tab, make_icon(SequenceBuilderTab.ICON_FILE), "Sequence")
        self.addTab(self.oven_tab, make_icon(OvenControlTab.ICON_FILE), "Oven")
        self.addTab(self.gamry_tab, make_icon("lightning.png"), "Gamry")

    def closeEvent(self, event: QCloseEvent | None):  # overridden
        if event is not None:
            for tab in (self.sequence_tab, self.oven_tab, self.gamry_tab):
                tab.save_on_close()
        super().closeEvent(event)
