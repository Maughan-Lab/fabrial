import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from tendo.singleton import SingleInstance, SingleInstanceException

from fabrial.constants import PACKAGE_NAME, icons
from fabrial.constants.paths import FOLDERS_TO_CREATE
from fabrial.custom_widgets.settings import ApplicationSettingsWindow
from fabrial.main_window import MainWindow
from fabrial.utility import errors, plugins as plugin_util


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

        appid = f"maughangroup.{PACKAGE_NAME}"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except ImportError:
        pass


def main():
    me = check_for_other_instances()  # noqa
    make_application_folders()
    errors.set_up_logging()
    sys.excepthook = errors.exception_handler  # log all uncaught exceptions
    fix_windows_sucking()
    # suppress Qt warnings (there's a bug in 6.9.1 that generates unnecessary warnings when the
    # window is resized)
    errors.suppress_warnings()
    # make the app first
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(icons.MAIN_ICON_FILE)))
    # then load plugins
    category_items, settings_widgets, plugin_settings = plugin_util.load_all_plugins()
    # then make the main window
    main_window = MainWindow(
        category_items, ApplicationSettingsWindow(plugin_settings, settings_widgets)
    )
    main_window.showMaximized()
    # run the application
    app.exec()

    # check to relaunch
    if main_window.should_relaunch:
        del me  # make sure the singleton is cleared
        # replace the current process with a new version of this one
        # first two arguments are both the python interpreter path
        # the third argument is this file
        # the remaining arguments are command line arguments except for the file name
        # this is all necessary so this function works with both when launching via fabrial.exe
        # and via python run.py/main.py
        os.execl(sys.executable, sys.executable, __file__, *sys.argv[1:])


if __name__ == "__main__":
    main()
