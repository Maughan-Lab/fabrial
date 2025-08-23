import json
import os

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QVBoxLayout

from fabrial import SAVED_DATA_FOLDER, PluginSettingsWidget

# create constants for where the settings are stored
SETTINGS_FOLDER = SAVED_DATA_FOLDER.joinpath("random_data")
SETTINGS_FILE = SETTINGS_FOLDER.joinpath("settings.json")
# create a constant for the name of the setting
PRINT_DATA_KEY = "print_data"

# this is a mutable global variable, so it should be behind a `Lock`. For the purposes of this
# example, we'll neglect that
SETTINGS: dict[str, bool] = {}


# we'll use this function later
def load_settings():
    """Loads the plugin's settings."""
    # try to load the settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            # modify the global variable
            settings = json.load(f)
            SETTINGS[PRINT_DATA_KEY] = settings[PRINT_DATA_KEY]
    except OSError:  # runs if the file doesn't exist; we'll assume we don't print data in this case
        pass


class RandomDataSettingsWidget(PluginSettingsWidget):
    """Settings widget for `random_data`."""

    def __init__(self):
        # don't forget to call the base `__init__()` method!
        PluginSettingsWidget.__init__(self)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # looks better
        self.setLayout(layout)
        # we'll use a checkbox to represent the settings
        self.print_data_checkbox = QCheckBox("Print Random Data")
        self.print_data_checkbox.setChecked(SETTINGS[PRINT_DATA_KEY])
        # whenever the checkbutton is checked/unchecked, update the global variable
        self.print_data_checkbox.toggled.connect(self.update_settings)
        layout.addWidget(self.print_data_checkbox)

    def update_settings(self, checked: bool):
        """Update the global settings variable."""
        SETTINGS[PRINT_DATA_KEY] = checked

    def window_close_event(self):  # overridden
        # this function gets called by Fabrial when the settings window closes. Here,
        # we'll use it to save our settings!
        try:
            # create the settings folder if it doesn't exist
            os.makedirs(SETTINGS_FOLDER, exist_ok=True)
            # save the data
            with open(SETTINGS_FILE, "w") as f:
                json.dump(SETTINGS, f)
        except OSError:
            pass  # if we fail, just do nothing
