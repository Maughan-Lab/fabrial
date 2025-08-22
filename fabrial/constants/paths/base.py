"""The base directory."""

from importlib import resources

from ..name import PACKAGE_NAME

with resources.path(PACKAGE_NAME) as path:
    BASE_FOLDER = path
    # TODO: remove
    # if not path.exists():  # this happens if we're frozen (packaged)
    #     # the path to the folder containing the executable
    #     BASE_FOLDER = Path(sys._MEIPASS)  # type: ignore
    # else:
    #     BASE_FOLDER = path

ASSETS_FOLDER = BASE_FOLDER.joinpath("assets")
