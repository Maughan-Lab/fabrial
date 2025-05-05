"""Filepaths for sequence settings."""

import os

from . import saved

SAVED_SETTINGS_FOLDER = os.path.join(saved.SAVED_SETTINGS_FOLDER, "sequence")

# files
SEQUENCE_AUTOSAVE_FILE = os.path.join(SAVED_SETTINGS_FOLDER, "sequence_autosave.json")
OPTIONS_STATE_AUTOSAVE_FILE = os.path.join(SAVED_SETTINGS_FOLDER, "options_state_autosave.json")
SEQUENCE_DIRECTORY_FILE = os.path.join(SAVED_SETTINGS_FOLDER, "sequence_directory.csv")
NON_EMPTY_DIRECTORY_WARNING_FILE = os.path.join(
    SAVED_SETTINGS_FOLDER, "non_empty_directory_warning.csv"
)
