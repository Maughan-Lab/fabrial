from pathlib import Path

from ...name import PACKAGE_NAME

SAVED_DATA_FOLDER = Path.home().joinpath("." + PACKAGE_NAME)
CORE_SETTINGS_FOLDER = SAVED_DATA_FOLDER.joinpath("core_settings")
