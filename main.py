import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from src import Files
from src.gamry_integration.Gamry import GAMRY
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
    for folder in Files.FOLDERS_TO_CREATE:
        os.makedirs(folder, exist_ok=True)


def main(main_window_type: type[MainWindow] = MainWindow):
    update_id()
    make_application_folders()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(Files.Icons.MAIN_ICON))
    # create the main window using `main_window_type`
    main_window = main_window_type()  # necessary for testing
    main_window.showMaximized()

    # catch all exceptions
    sys.excepthook = generate_exception_handler(main_window)
    # run Quincy
    app.exec()
    # close GamryCOM
    GAMRY.cleanup()


if __name__ == "__main__":
    main()
