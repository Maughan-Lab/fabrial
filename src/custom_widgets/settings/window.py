from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QTabWidget, QVBoxLayout

from ...Files import APPLICATION_NAME

if TYPE_CHECKING:
    from ...main_window import MainWindow

from ...tabs.oven_control import OvenControlTab
from ...tabs.sequence_builder import SequenceBuilderTab
from ...utility.images import make_icon
from ..augmented.button import BiggerButton
from ..container import Container
from .gamry import GamrySettingsTab
from .oven import OvenSettingsTab
from .sequence import SequenceSettingsTab


class ApplicationSettingsWindow(Container):
    """Settings window the application's settings."""

    def __init__(self, main_window: MainWindow) -> None:
        self.main_window = main_window
        layout = QVBoxLayout()
        super().__init__(layout)
        self.setWindowTitle(f"{APPLICATION_NAME} - Settings")

        tab_widget = QTabWidget(self)
        self.sequence_tab = SequenceSettingsTab()
        self.oven_tab = OvenSettingsTab()
        self.gamry_tab = GamrySettingsTab()
        tab_widget.addTab(self.sequence_tab, make_icon(SequenceBuilderTab.ICON_FILE), "Sequence")
        tab_widget.addTab(self.oven_tab, make_icon(OvenControlTab.ICON_FILE), "Oven")
        tab_widget.addTab(self.gamry_tab, make_icon("lightning.png"), "Gamry")
        layout.addWidget(tab_widget)

        layout.addWidget(
            BiggerButton("Relaunch", self.handle_relaunch_request, size_scalars=(2, 2)),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

    def handle_relaunch_request(self):
        """Runs when the relaunch button is pressed."""
        self.main_window.set_relaunch(True)
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent | None):  # overridden
        if event is not None:
            for tab in (self.sequence_tab, self.oven_tab, self.gamry_tab):
                tab.save_on_close()
        super().closeEvent(event)
