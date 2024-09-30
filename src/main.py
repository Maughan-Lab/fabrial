from main_window import MainWindow
from PyQt6.QtWidgets import QApplication
from temperature_sensor import Oven
from instruments import InstrumentSet

import sys


def main():
    # create instruments
    instruments = InstrumentSet(Oven("XXXX"), None)
    # pass in any provided system arguments
    app = QApplication(sys.argv)
    main_window = MainWindow(instruments)

    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
