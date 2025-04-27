from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.main_window import MainWindow
from src import Files
from src.gamry_integration.Gamry import GAMRY
import sys
import os


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
    for folder in Files.FOLDERS_TO_CREATE:
        os.makedirs(folder, exist_ok=True)


def main(main_window_type: type[MainWindow] = MainWindow):
    update_id()
    make_application_folders()

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(Files.Icons.MAIN_ICON))
    # create the main window using `main_window_type`
    main_window = main_window_type()  # necessary for testing
    main_window.show()
    # run Quincy
    app.exec()
    # close GamryCOM
    GAMRY.cleanup()


if __name__ == "__main__":
    main()
