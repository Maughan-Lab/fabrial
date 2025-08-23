from __future__ import annotations

from collections.abc import Mapping

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QShowEvent
from PyQt6.QtWidgets import QTabWidget, QVBoxLayout

from ...constants import APP_NAME
from ...tabs import sequence_builder
from ...utility import images
from ...utility.plugins import PluginSettings
from ..augmented import Button, Widget
from .plugin_settings_tab import PluginSettingsTab
from .plugin_settings_widget import PluginSettingsWidget
from .sequence_settings_tab import SequenceSettingsTab


class ApplicationSettingsWindow(Widget):
    """Settings window the application's settings."""

    relaunchRequested = pyqtSignal()
    """Emitted when the user requests to relaunch the application. No arguments."""

    def __init__(
        self,
        plugin_settings: PluginSettings,
        plugin_settings_widgets: Mapping[str, PluginSettingsWidget],
    ) -> None:
        layout = QVBoxLayout()
        Widget.__init__(self, layout)
        self.setWindowTitle(f"{APP_NAME} - Settings")

        tab_widget = QTabWidget(self)
        tab_widget.setDocumentMode(True)
        layout.addWidget(tab_widget)
        # tab for the sequence
        self.sequence_settings_tab = SequenceSettingsTab()
        tab_widget.addTab(
            self.sequence_settings_tab, images.make_icon(sequence_builder.ICON_FILENAME), "Sequence"
        )
        # tab for plugins
        self.plugin_settings_tab = PluginSettingsTab(plugin_settings, plugin_settings_widgets)
        tab_widget.addTab(self.plugin_settings_tab, images.make_icon("lightning.png"), "Plugins")
        # a button to relaunch the application
        relaunch_button = Button("Relaunch", self.relaunchRequested.emit)
        relaunch_button.setMinimumSize(relaunch_button.sizeHint() * 2)  # make it bigger
        layout.addWidget(relaunch_button, alignment=Qt.AlignmentFlag.AlignRight)

        # if this window is open you can't access the rest of the application
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

    def showEvent(self, event: QShowEvent | None):  # overridden
        if event is not None:
            self.sequence_settings_tab.window_open_event()
            self.plugin_settings_tab.window_open_event()

        Widget.showEvent(self, event)

    def closeEvent(self, event: QCloseEvent | None):  # overridden
        if event is not None:
            self.sequence_settings_tab.save_on_close()
            self.plugin_settings_tab.save_on_close()
        Widget.closeEvent(self, event)
