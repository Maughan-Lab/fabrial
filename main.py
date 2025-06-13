import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from tendo.singleton import SingleInstance, SingleInstanceException

from src.Files import FOLDERS_TO_CREATE, Icons
from src.gamry_integration.gamry import GAMRY
from src.instruments import INSTRUMENTS
from src.main_window import MainWindow
from src.utility.errors import generate_exception_handler


def update_id():
    """
    On Windows, this will make the application icon show up in the task bar. It does nothing on
    other platforms.
    """
    try:
        from ctypes import windll  # Only exists on Windows.

        appid = "maughangroup.quincy.1"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
    except ImportError:
        pass


def make_application_folders():
    """Create folders for the application."""
    for folder in FOLDERS_TO_CREATE:
        os.makedirs(folder, exist_ok=True)


def main(main_window_type: type[MainWindow] = MainWindow):
    try:
        me = SingleInstance()  # noqa
    except SingleInstanceException:
        sys.exit()

    update_id()
    make_application_folders()

    # create application
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(Icons.MAIN_ICON))
    # create the main window using `main_window_type`
    main_window = main_window_type()  # necessary for testing
    main_window.showMaximized()
    # catch all exceptions
    sys.excepthook = generate_exception_handler(main_window)
    # run Quincy
    app.exec()
    # stop the oven's thread
    INSTRUMENTS.oven.stop()
    # close GamryCOM
    GAMRY.cleanup()

    # check to relaunch
    if main_window.should_relaunch():
        del me  # make sure the singleton is cleared
        # replace the current process with a new version of this one
        os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == "__main__":
    main()
