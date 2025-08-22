from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QApplication, QTabWidget, QVBoxLayout

from ...constants import APP_NAME

if TYPE_CHECKING:
    from ...main_window import MainWindow

from ...tabs import sequence_builder
from ...utility import images
from ..augmented import BiggerButton, Widget
from .sequence import SequenceSettingsTab


class ApplicationSettingsWindow(Widget):
    """Settings window the application's settings."""

    def __init__(self, main_window: MainWindow) -> None:
        self.main_window = main_window
        layout = QVBoxLayout()
        Widget.__init__(self, layout)
        self.setWindowTitle(f"{APP_NAME} - Settings")

        tab_widget = QTabWidget(self)
        layout.addWidget(tab_widget)
        # tab for the sequence
        self.sequence_settings_tab = SequenceSettingsTab(self)
        tab_widget.addTab(
            self.sequence_settings_tab, images.make_icon(sequence_builder.ICON_FILENAME), "Sequence"
        )
        # a button to relaunch the application
        layout.addWidget(
            BiggerButton("Relaunch", self.handle_relaunch_request, size_scalars=(2, 2)),
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

    def handle_relaunch_request(self):
        """Runs when the relaunch button is pressed."""
        self.main_window.relaunch = True
        QApplication.quit()

    def closeEvent(self, event: QCloseEvent | None):  # overridden
        if event is not None:
            self.sequence_settings_tab.save_on_close()
        Widget.closeEvent(self, event)
