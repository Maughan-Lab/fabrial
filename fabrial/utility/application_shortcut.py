import sys
from pathlib import Path

from fabrial.constants import APP_NAME, PACKAGE_NAME
from fabrial.constants.paths.icons import PACKAGE_ICON_FILE

# mypy does not like this file, I promise it works properly


def create_application_shortcut():
    """Create a system shortcut that can be used to launch the application."""
    try:
        import pyshortcuts  # type: ignore
    except Exception:
        raise NameError(
            f"Please use `pip install {PACKAGE_NAME}[shortcut]` to install the shortcut "
            "dependencies"
        )

    pyshortcuts.make_shortcut(  # type: ignore
        str(Path(sys.executable).parent.joinpath(f"{PACKAGE_NAME}-gui-only")),
        name=APP_NAME,
        icon=str(PACKAGE_ICON_FILE),
        terminal=False,
        desktop=False,
    )
