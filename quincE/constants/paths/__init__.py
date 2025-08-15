"""File paths for the application."""

from . import descriptions, icons, settings
from .base import ASSETS, PLUGINS

FOLDERS_TO_CREATE = [
    settings.saved.SAVED_SETTINGS,
    settings.oven.SAVED_SETTINGS_FOLDER,
    settings.sequence.SAVED_SETTINGS_FOLDER,
    settings.gamry.SAVED_SETTINGS_FOLDER,
]
