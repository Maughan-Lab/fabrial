"""Filepaths and dictionary keys for Gamry settings."""

from .defaults import DEFAULT_SETTINGS
from .saved import SAVED_SETTINGS

SETTINGS_FOLDER_NAME = "gamry"
SETTINGS_FILENAME = "gamry_settings.json"

# files
SAVED_SETTINGS_FOLDER = SAVED_SETTINGS.joinpath(SETTINGS_FOLDER_NAME)
SAVED_SETTINGS_FILE = SAVED_SETTINGS.joinpath(SETTINGS_FILENAME)
DEFAULT_SETTINGS_FILE = DEFAULT_SETTINGS.joinpath(SETTINGS_FOLDER_NAME, SETTINGS_FILENAME)
DESCRIPTION_FOLDER = DEFAULT_SETTINGS.joinpath(SETTINGS_FOLDER_NAME)
DESCRIPTION_FILENAME = "description.md"
# keys
ENABLED = "Enabled"
LOCATION = "GamryCOM Location"
# other
DEFAULT_GAMRY_LOCATION = "C:/Program Files (x86)/Gamry Instruments/Framework/GamryCom.exe"
