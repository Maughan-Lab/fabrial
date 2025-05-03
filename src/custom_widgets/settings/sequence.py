from PyQt6.QtWidgets import QCheckBox, QFormLayout

from ... import Files
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
            with open(Files.SavedSettings.Sequence.NON_EMPTY_DIRECTORY_WARNING, "r") as f:
                if f.read().strip() == str(True):
                    self.non_empty_directory_warning_checkbox.setChecked(True)
        except Exception:
            pass

        layout.addWidget(self.non_empty_directory_warning_checkbox)

    def save_on_close(self):
        """Call this when closing the settings window to save settings."""
        with open(Files.SavedSettings.Sequence.NON_EMPTY_DIRECTORY_WARNING, "w") as f:
            f.write(str(self.non_empty_directory_warning_checkbox.isChecked()))
