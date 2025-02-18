from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from instruments import Oven, InstrumentSet
import Files
import sys
import os

# on windows, this will make the application icon show up in the task bar
# it does nothing on other platforms
try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "maughangroup.quincy.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass

FOLDERS_TO_CREATE = (Files.SAVED_SETTINGS_FOLDER, Files.Sequence.DATA_FOLDER)


def main():
    # create any folders that need to exist
    for folder in FOLDERS_TO_CREATE:
        os.makedirs(folder, exist_ok=True)
    # create instruments
    instruments = InstrumentSet(Oven(), None)
    # pass in any provided system arguments
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(Files.ICON))

    main_window = MainWindow(instruments)
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()
