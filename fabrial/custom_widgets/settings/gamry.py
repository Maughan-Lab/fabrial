import json
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QFileDialog, QHBoxLayout, QVBoxLayout

from ...constants import APP_NAME
from ...constants.paths.settings import gamry
from ...gamry_integration import GAMRY
from ...utility import images, layout as layout_util
from ..augmented import Button, IconLabel, OkCancelDialog
from .settings_description import SettingsDescriptionWidget


class GamrySettingsTab(SettingsDescriptionWidget):
    """Gamry-related settings."""

    def __init__(self):
        try:
            with open(gamry.SAVED_SETTINGS_FILE, "r") as f:
                settings_dict = json.load(f)
        except Exception:
            with open(gamry.DEFAULT_SETTINGS_FILE, "r") as f:
                settings_dict = json.load(f)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        SettingsDescriptionWidget.__init__(self, layout)

        self.set_description_from_file(
            gamry.DESCRIPTION_FOLDER,
            gamry.DESCRIPTION_FILENAME,
            {"APPLICATION_NAME": APP_NAME},
        )

        self.enabled_checkbox = QCheckBox("Enable Gamry features")
        self.enabled_checkbox.setChecked(settings_dict[gamry.ENABLED])
        layout.addWidget(self.enabled_checkbox)

        self.gamry_location_label = IconLabel(
            images.make_pixmap("document-code.png"), settings_dict[gamry.LOCATION]
        )
        button_layout = layout_util.add_sublayout(layout, QHBoxLayout())
        self.gamry_location_button = Button("Select GamryCOM Location", self.choose_gamry_location)
        self.gamry_location_label.label().setWordWrap(True)
        self.default_location_button = Button(
            "Default Location",
            lambda: self.gamry_location_label.label().setText(gamry.DEFAULT_GAMRY_LOCATION),
        )
        layout_util.add_to_layout(
            button_layout, self.gamry_location_button, self.default_location_button
        )
        layout.addWidget(self.gamry_location_label)

        self.enabled_checkbox.stateChanged.connect(
            lambda checked: self.gamry_location_button.setEnabled(checked)
        )

        if self.enabled_checkbox.isChecked() and not GAMRY.is_valid():
            if OkCancelDialog(
                "Error",
                (
                    "Unable to load GamryCOM.\n"
                    f"{APP_NAME} will launch without Gamry features. You may change "
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
            os.path.dirname(gamry.DEFAULT_GAMRY_LOCATION),
            "Executables (*.exe)",
        )[0]
        if filepath != "":
            self.gamry_location_label.label().setText(filepath)

    def save_on_close(self):
        """Call this when closing the settings window to save settings."""
        settings_dict = {
            gamry.ENABLED: self.enabled_checkbox.isChecked(),
            gamry.LOCATION: self.gamry_location_label.label().text(),
        }
        with open(gamry.SAVED_SETTINGS_FILE, "w") as f:
            json.dump(settings_dict, f)
