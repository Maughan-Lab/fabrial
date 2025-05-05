"""Filepaths and dictionary keys for Gamry settings."""

import os

from . import saved
from .defaults import DEFAULT_SETTINGS_FOLDER

SETTINGS_FOLDER_NAME = "gamry"
SETTINGS_FILENAME = "gamry_settings.json"

# files
SAVED_SETTINGS_FOLDER = os.path.join(saved.SAVED_SETTINGS_FOLDER, SETTINGS_FOLDER_NAME)
SAVED_SETTINGS_FILE = os.path.join(SAVED_SETTINGS_FOLDER, SETTINGS_FILENAME)
DEFAULT_SETTINGS_FILE = os.path.join(
    DEFAULT_SETTINGS_FOLDER, SETTINGS_FOLDER_NAME, SETTINGS_FILENAME
)
DESCRIPTION_FOLDER = os.path.join(DEFAULT_SETTINGS_FOLDER, SETTINGS_FOLDER_NAME)
DESCRIPTION_FILENAME = "description.md"
# keys
ENABLED = "Enabled"
LOCATION = "GamryCOM Location"
# other
DEFAULT_GAMRY_LOCATION = "C:/Program Files (x86)/Gamry Instruments/Framework/GamryCom.exe"
