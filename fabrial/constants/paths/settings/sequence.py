"""Filepaths for sequence settings."""

from .saved_data import CORE_SETTINGS_FOLDER

SEQUENCE_SETTINGS_FOLDER = CORE_SETTINGS_FOLDER.joinpath("sequence")

# files
SEQUENCE_ITEMS_FILE = SEQUENCE_SETTINGS_FOLDER.joinpath("sequence_items_autosave.json")
SEQUENCE_STATE_FILE = SEQUENCE_SETTINGS_FOLDER.joinpath("sequence_state_autosave.json")
OPTIONS_STATE_FILE = SEQUENCE_SETTINGS_FOLDER.joinpath("options_state_autosave.json")
SEQUENCE_DIRECTORY_FILE = SEQUENCE_SETTINGS_FOLDER.joinpath("sequence_directory.json")
NON_EMPTY_DIRECTORY_WARNING_FILE = SEQUENCE_SETTINGS_FOLDER.joinpath(
    "non_empty_directory_warning.json"
)
