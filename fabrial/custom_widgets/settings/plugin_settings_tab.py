import json
import logging
import typing
from collections.abc import Callable, Mapping
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLayoutItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ...constants.paths.settings.plugins import GLOBAL_PLUGINS_FILE, LOCAL_PLUGINS_FILE
from ...utility import errors
from ...utility.plugins import PluginSettings
from ..augmented import Button, Label, Widget
from ..container import Container
from .plugin_settings_widget import PluginSettingsWidget


class LocalPluginManager(Container):
    """Manages local plugins."""

    def __init__(self, local_plugin_settings: Mapping[str, bool]):
        self.widget_layout = QGridLayout()
        Container.__init__(self, self.widget_layout)

        def uninstall_function_factory(plugin_name: str) -> Callable[[], None]:
            return lambda: self.uninstall_plugin(plugin_name)

        for i, (plugin_name, enabled) in enumerate(local_plugin_settings.items()):
            self.widget_layout.addWidget(Label(plugin_name), i, 0)

            check_box = QCheckBox("Enabled")
            check_box.setChecked(enabled)
            self.widget_layout.addWidget(check_box, i, 1)

            self.widget_layout.addWidget(
                Button("Uninstall", uninstall_function_factory(plugin_name)), i, 2
            )

    def install_plugin(self, plugin_folder: Path):
        """
        Install a local plugin from **plugin_folder**. Logs errors and notifies the user of failure.
        """
        return False

    def uninstall_plugin(self, plugin_name: str):
        """Uninstall a local plugin. Logs errors and notifies the user of failure."""
        # TODO: try to uninstall plugin first (you have to check for the folder name)

        for i in range(self.widget_layout.rowCount()):
            item = self.widget_layout.itemAtPosition(i, 0)
            if item is None:
                continue
            label = typing.cast(Label, item.widget())
            if label.text() == plugin_name:
                column_count = self.widget_layout.columnCount()
                for j in range(column_count):
                    widget = typing.cast(
                        QWidget,
                        typing.cast(QLayoutItem, self.widget_layout.itemAtPosition(i, j)).widget(),
                    )
                    widget.setParent(None)
                    widget.deleteLater()
                break
        else:  # the loop ended naturally; this should never run
            raise LookupError("Requested plugin name was not present. This is a bug")

    def save_on_close(self):
        """Save the local plugin settings on close."""
        try:
            with open(LOCAL_PLUGINS_FILE, "w") as f:
                json.dump(widgets_to_plugin_settings(self.widget_layout, 1), f)
        except OSError:
            logging.getLogger(__name__).warning("Failed to save local plugin settings")


class PluginManagementWidget(Widget):
    """Widget for managing plugins (i.e. if they are enabled, installing/uninstalling, etc.)."""

    def __init__(self, plugin_settings: PluginSettings):
        layout = QVBoxLayout()
        Widget.__init__(self, layout)

        header_font = QApplication.font()
        header_font.setBold(True)

        self.local_manager = LocalPluginManager(plugin_settings.local_settings)
        self.global_manager = None  # TODO

        local_plugin_layout = QHBoxLayout()
        local_label = Label("Local Plugins")
        local_label.setFont(header_font)
        local_plugin_layout.addWidget(local_label, alignment=Qt.AlignmentFlag.AlignLeft)
        local_plugin_layout.addWidget(
            Button("Install Local Plugin"), alignment=Qt.AlignmentFlag.AlignRight
        )
        layout.addLayout(local_plugin_layout)
        layout.addWidget(
            self.local_manager, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

    def save_on_close(self):
        """Save settings on close."""
        self.local_manager.save_on_close()


class PluginSettingsTab(QTabWidget):
    """Tab in the settings window for plugins."""

    def __init__(
        self,
        plugin_settings: PluginSettings,
        plugin_settings_widgets: Mapping[str, PluginSettingsWidget],
    ):
        QTabWidget.__init__(self)
        self.plugin_settings_widgets = plugin_settings_widgets

        self.plugin_manager = PluginManagementWidget(plugin_settings)
        self.addTab(self.plugin_manager, "General")

        for plugin_name, widget in self.plugin_settings_widgets.items():
            self.addTab(widget, plugin_name)

    def window_open_event(self):
        """Call this when the settings window is opened."""
        for widget in self.plugin_settings_widgets.values():
            widget.window_open_event()

    def save_on_close(self):
        """Save settings on close."""
        self.plugin_manager.save_on_close()
        for widget in self.plugin_settings_widgets.values():
            widget.window_close_event()


def widgets_to_plugin_settings(layout: QGridLayout, check_box_index: int) -> dict[str, bool]:
    """
    Extract plugin settings from the layout.

    Parameters
    ----------
    layout
        The layout containing the plugin name labels and "enabled" checkboxes. Plugin name labels
        should be at index 0 in each row.
    check_box_index
        The index of the "enabled" checkbox in each row of the layout.
    """
    plugin_settings: dict[str, bool] = {}

    for i in range(layout.rowCount()):
        label_item = layout.itemAtPosition(i, 0)
        if label_item is None:
            continue  # ignore the row
        label = typing.cast(Label, label_item.widget())
        check_box = typing.cast(
            QCheckBox, typing.cast(QLayoutItem, layout.itemAtPosition(i, check_box_index)).widget()
        )
        plugin_settings[label.text()] = check_box.isChecked()

    return plugin_settings
