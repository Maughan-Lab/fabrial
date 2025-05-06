from PyQt6.QtWidgets import QCheckBox, QFormLayout

from ...Files import Settings
from ..augmented.widget import Widget


class SequenceSettingsTab(Widget):
    """Settings related to the sequence."""

    def __init__(self):
        layout = QFormLayout()
        super().__init__(layout)
        self.non_empty_directory_warning_checkbox = QCheckBox(
            "Show a warning when starting the sequence with a non-empty data directory."
        )
        try:
            with open(Settings.Sequence.NON_EMPTY_DIRECTORY_WARNING_FILE, "r") as f:
                if f.read().strip() == str(True):
                    self.non_empty_directory_warning_checkbox.setChecked(True)
        except Exception:
            self.non_empty_directory_warning_checkbox.setChecked(True)

        layout.addWidget(self.non_empty_directory_warning_checkbox)

    def save_on_close(self):
        """Call this when closing the settings window to save settings."""
        with open(Settings.Sequence.NON_EMPTY_DIRECTORY_WARNING_FILE, "w") as f:
            f.write(str(self.non_empty_directory_warning_checkbox.isChecked()))
