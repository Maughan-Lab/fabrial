from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from instruments import Oven, InstrumentSet
from file_locations import ICON_FILE
import sys

# on windows, this will make the application icon show up in the task bar
# it does nothing on other platforms
try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "maughangroup.quincy.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


def main():
    # create instruments
    instruments = InstrumentSet(Oven("XXXX"), None)
    # pass in any provided system arguments
    app = QApplication(sys.argv)

    app.setWindowIcon(QIcon(ICON_FILE))

    main_window = MainWindow(instruments)
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()
