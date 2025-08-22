from __future__ import annotations

import json
import typing
from typing import TYPE_CHECKING

from PyQt6.QtCore import QEvent, QObject, Qt
from PyQt6.QtWidgets import QCheckBox, QVBoxLayout

from ...constants.paths import settings
from ..augmented import Widget

if TYPE_CHECKING:
    from .window import ApplicationSettingsWindow


class SequenceSettingsTab(Widget):
    """Settings related to the sequence."""

    def __init__(self, window: ApplicationSettingsWindow):
        self.settings_window = window
        layout = QVBoxLayout()
        Widget.__init__(self, layout)
        self.non_empty_directory_warning_checkbox = QCheckBox(
            "Show a warning when starting the sequence with a non-empty data directory."
        )

        layout.addWidget(
            self.non_empty_directory_warning_checkbox, alignment=Qt.AlignmentFlag.AlignTop
        )
        window.installEventFilter(self)  # read events from the window

    def eventFilter(self, obj: QObject | None, event: QEvent | None) -> bool:  # overridden
        # whenever the window is shown, update the checkbox
        if obj is self.settings_window and event is not None and event.type() == QEvent.Type.Show:
            try:
                with open(settings.sequence.NON_EMPTY_DIRECTORY_WARNING_FILE, "r") as f:
                    checked = typing.cast(bool, json.load(f))
            except Exception:  # if we can't read the file assume we should show the warning
                checked = True
            self.non_empty_directory_warning_checkbox.setChecked(checked)

        return Widget.eventFilter(self, obj, event)

    def save_on_close(self):
        """Call this when closing the settings window to save settings."""
        try:
            with open(settings.sequence.NON_EMPTY_DIRECTORY_WARNING_FILE, "w") as f:
                json.dump(self.non_empty_directory_warning_checkbox.isChecked(), f)
        except Exception:
            pass
