import json
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QFileDialog, QHBoxLayout, QVBoxLayout

from ...Files import APPLICATION_NAME, Settings
from ...gamry_integration.gamry import GAMRY
from ...utility.images import make_pixmap
from ...utility.layouts import add_sublayout, add_to_layout
from ..augmented.button import Button
from ..augmented.dialog import OkCancelDialog
from ..augmented.label import IconLabel
from .settings_description import SettingsDescriptionWidget

SettingNames = Settings.Gamry


class GamrySettingsTab(SettingsDescriptionWidget):
    """Gamry-related settings."""

    def __init__(self):
        try:
            with open(Settings.Gamry.SAVED_SETTINGS_FILE, "r") as f:
                settings_dict = json.load(f)
        except Exception:
            with open(Settings.Gamry.DEFAULT_SETTINGS_FILE, "r") as f:
                settings_dict = json.load(f)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        super().__init__(layout)

        self.set_description_from_file(
            Settings.Gamry.DESCRIPTION_FOLDER,
            Settings.Gamry.DESCRIPTION_FILENAME,
            {"APPLICATION_NAME": APPLICATION_NAME},
        )

        self.enabled_checkbox = QCheckBox("Enable Gamry features")
        self.enabled_checkbox.setChecked(settings_dict[SettingNames.ENABLED])
        layout.addWidget(self.enabled_checkbox)

        self.gamry_location_label = IconLabel(
            make_pixmap("document-code.png"), settings_dict[SettingNames.LOCATION]
        )
        button_layout = add_sublayout(layout, QHBoxLayout)
        self.gamry_location_button = Button("Select GamryCOM Location", self.choose_gamry_location)
        self.gamry_location_label.label().setWordWrap(True)
        self.default_location_button = Button(
            "Default Location",
            lambda: self.gamry_location_label.label().setText(
                Settings.Gamry.DEFAULT_GAMRY_LOCATION
            ),
        )
        add_to_layout(button_layout, self.gamry_location_button, self.default_location_button)
        layout.addWidget(self.gamry_location_label)

        self.enabled_checkbox.stateChanged.connect(
            lambda checked: self.gamry_location_button.setEnabled(checked)
        )

        if self.enabled_checkbox.isChecked() and not GAMRY.is_valid():
            if OkCancelDialog(
                "Error",
                (
                    "Unable to load GamryCOM.\n"
                    f"{APPLICATION_NAME} will launch without Gamry features. You may change "
                    "this in the settings."
                ),
            ).run():
                self.enabled_checkbox.setChecked(False)
                self.save_on_close()
            else:
                sys.exit()

    def choose_gamry_location(self):
        """Select the location of GamryCOM."""
        filepath = QFileDialog.getOpenFileName(
            self,
            "Choose GamryCOM location",
            os.path.dirname(Settings.Gamry.DEFAULT_GAMRY_LOCATION),
            "Executables (*.exe)",
        )[0]
        if filepath != "":
            self.gamry_location_label.label().setText(filepath)

    def save_on_close(self):
        """Call this when closing the settings window to save settings."""
        settings_dict = {
            SettingNames.ENABLED: self.enabled_checkbox.isChecked(),
            SettingNames.LOCATION: self.gamry_location_label.label().text(),
        }
        with open(Settings.Gamry.SAVED_SETTINGS_FILE, "w") as f:
            json.dump(settings_dict, f)
