import os
import sys
from types import ModuleType
from typing import Iterable

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from tendo.singleton import SingleInstance, SingleInstanceException

from .constants import icons
from .constants.paths import FOLDERS_TO_CREATE
from .gamry_integration import GAMRY
from .instruments import INSTRUMENTS
from .main_window import MainWindow
from .utility import errors, plugins


def make_application_folders():
    """Create folders for the application."""
    for folder in FOLDERS_TO_CREATE:
        os.makedirs(folder, exist_ok=True)


def check_for_other_instances() -> SingleInstance:
    """
    Attempt to create a singleton so only once instance of the application can run. If an instance
    is already running, this exits the application.
    """
    try:
        return SingleInstance()
    except SingleInstanceException:
        sys.exit()


def fix_windows_sucking():
    """Make the application show up in the taskbar on Windows (because Windows sucks)."""
    try:
        from ctypes import windll  # only exists on Windows

        appid = "maughangroup.quincy.1"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except ImportError:
        pass


def load_plugins() -> list[ModuleType]:
    """Load all plugins."""
    plugin_modules, installed_failures, local_failures = plugins.load_all_plugins()
    if len(installed_failures) > 0 or len(local_failures) > 0:
        message = ""
        if len(installed_failures) > 0:
            message += f"Failed to load installed plugins:\n\n{", ".join(installed_failures)}\n\n"
        if len(local_failures) > 0:
            message += f"Failed to load local plugins:\n\n{", ".join(local_failures)}\n\n"
        message += "See the error log for details."
        errors.show_error_delayed("Plugin Error", message)

    return plugin_modules


def make_app(plugin_modules: Iterable[ModuleType]) -> tuple[QApplication, MainWindow]:
    """Make the application."""
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(icons.MAIN_ICON)))
    main_window = MainWindow(plugin_modules)
    main_window.showMaximized()
    return (app, main_window)


def main():
    print("HOOA")
    me = check_for_other_instances()  # noqa
    sys.excepthook = errors.exception_handler  # log all uncaught exceptions
    fix_windows_sucking()
    make_application_folders()
    # suppress Qt warnings (there is a bug that generates warnings when the window is resized)
    errors.suppress_warnings()
    plugin_modules = load_plugins()
    app, main_window = make_app(plugin_modules)
    # run the application
    app.exec()
    # TODO: remove these
    # stop the oven's thread
    INSTRUMENTS.oven.stop()
    # close GamryCOM
    GAMRY.cleanup()

    # check to relaunch
    if main_window.should_relaunch():
        del me  # make sure the singleton is cleared
        # replace the current process with a new version of this one
        os.execl(sys.executable, sys.executable, *sys.argv)
