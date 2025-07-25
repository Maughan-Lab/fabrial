"""Filepaths for sequence settings."""

from .saved import SAVED_SETTINGS

SAVED_SETTINGS_FOLDER = SAVED_SETTINGS.joinpath("sequence")

# files
SEQUENCE_AUTOSAVE_FILE = SAVED_SETTINGS_FOLDER.joinpath("sequence_autosave.json")
OPTIONS_STATE_AUTOSAVE_FILE = SAVED_SETTINGS_FOLDER.joinpath("options_state_autosave.json")
SEQUENCE_DIRECTORY_FILE = SAVED_SETTINGS_FOLDER.joinpath("sequence_directory.csv")
NON_EMPTY_DIRECTORY_WARNING_FILE = SAVED_SETTINGS_FOLDER.joinpath("non_empty_directory_warning.csv")
