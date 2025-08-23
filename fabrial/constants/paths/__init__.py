"""File paths for the application."""

from . import descriptions, icons, settings
from .base import ASSETS_FOLDER
from .settings.plugins import GLOBAL_PLUGINS_FOLDER, PLUGIN_SETTINGS_FOLDER
from .settings.saved_data import SAVED_DATA_FOLDER
from .settings.sequence import SEQUENCE_SETTINGS_FOLDER

FOLDERS_TO_CREATE = [
    SAVED_DATA_FOLDER,
    SEQUENCE_SETTINGS_FOLDER,
    PLUGIN_SETTINGS_FOLDER,
    GLOBAL_PLUGINS_FOLDER,
]
