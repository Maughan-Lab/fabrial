from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.main_window import MainWindow
from src.instruments import Oven, InstrumentSet
from src import Files
import sys
import os

FOLDERS_TO_CREATE = (Files.SAVED_SETTINGS_FOLDER, Files.Sequence.DATA_FOLDER)


def update_id():
    # on windows, this will make the application icon show up in the task bar
    # it does nothing on other platforms
    try:
        from ctypes import windll  # Only exists on Windows.

        myappid = "maughangroup.quincy.1"
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass


def make_application_folders():
    for folder in FOLDERS_TO_CREATE:
        os.makedirs(folder, exist_ok=True)


def main(oven_type: type[Oven] = Oven, main_window_type: type[MainWindow] = MainWindow):
    update_id()
    make_application_folders()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(Files.ICON))
    # create the instrument using `oven_type`
    instruments = InstrumentSet(oven_type(), None)  # necessary for testing
    # create the main window using `main_window_type`
    main_window = main_window_type(instruments)  # necessary for testing
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()
