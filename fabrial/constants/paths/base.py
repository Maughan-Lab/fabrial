"""The base directory."""

import sys
from importlib import resources
from pathlib import Path

from ..name import PACKAGE_NAME

with resources.path(PACKAGE_NAME) as path:
    if not path.exists():  # this happens if we're frozen (packaged)
        # the path to the folder containing the executable
        FOLDER = Path(sys._MEIPASS)  # type: ignore
    else:
        FOLDER = path

ASSETS = FOLDER.joinpath("assets")
PLUGINS = FOLDER.joinpath("plugins")
