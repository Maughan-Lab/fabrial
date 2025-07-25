"""The base directory."""

import os
import sys
from importlib import resources
from pathlib import Path

with resources.path("quincy") as path:
    if not os.path.exists(path):  # this happens if we're frozen (packaged)
        # the path to the folder containing the executable
        FOLDER = Path(sys._MEIPASS)  # type: ignore
    else:
        FOLDER = path

ASSETS = FOLDER.joinpath("assets")
