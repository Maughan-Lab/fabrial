from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from instruments import Oven, InstrumentSet
import sys
import os

BASEDIR = os.path.dirname(__file__)


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

    icon_path = os.path.join(BASEDIR, "oven_icon.png")
    app.setWindowIcon(QIcon(icon_path))

    main_window = MainWindow(instruments)
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()
