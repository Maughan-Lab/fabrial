from . import Settings
from .Settings import saved

FOLDERS_TO_CREATE = [
    saved.SAVED_SETTINGS_FOLDER,
    Settings.Oven.SAVED_SETTINGS_FOLDER,
    Settings.Sequence.SAVED_SETTINGS_FOLDER,
    Settings.Gamry.SAVED_SETTINGS_FOLDER,
]
