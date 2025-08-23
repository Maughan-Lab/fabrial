from __future__ import annotations

import json
import typing

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QVBoxLayout

from ...constants.paths import settings
from ..augmented import Widget


class SequenceSettingsTab(Widget):
    """Settings related to the sequence."""

    def __init__(self):
        layout = QVBoxLayout()
        Widget.__init__(self, layout)
        self.non_empty_directory_warning_checkbox = QCheckBox(
            "Show a warning when starting the sequence with a non-empty data directory."
        )

        layout.addWidget(
            self.non_empty_directory_warning_checkbox, alignment=Qt.AlignmentFlag.AlignTop
        )

    def window_open_event(self):
        """Call this when the settings window is opened to refresh settings."""
        try:
            with open(settings.sequence.NON_EMPTY_DIRECTORY_WARNING_FILE, "r") as f:
                checked = typing.cast(bool, json.load(f))
        except Exception:  # if we can't read the file assume we should show the warning
            checked = True
        self.non_empty_directory_warning_checkbox.setChecked(checked)

    def save_on_close(self):
        """Call this when closing the settings window to save settings."""
        try:
            with open(settings.sequence.NON_EMPTY_DIRECTORY_WARNING_FILE, "w") as f:
                json.dump(self.non_empty_directory_warning_checkbox.isChecked(), f)
        except Exception:
            pass
