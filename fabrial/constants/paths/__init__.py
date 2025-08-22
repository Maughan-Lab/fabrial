"""File paths for the application."""

from . import descriptions, icons, settings
from .base import ASSETS, PLUGINS
from .settings.saved_data import SAVED_DATA_FOLDER

FOLDERS_TO_CREATE = [
    SAVED_DATA_FOLDER,
    settings.sequence.SEQUENCE_SETTINGS_FOLDER,
]
