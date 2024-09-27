# you may be wondering, "Why is there a folder called 'backend' where all of the actual source code
# is stored?" Because of Python's module system, I cannot organize the project logically without
# this folder, so we are dealing with that.

from main_window import MainWindow
from PyQt6.QtWidgets import QApplication
from change_setpoint.widgets import SetTempWidget
from temperature_sensor import Oven

import sys


def main():
    # create instruments
    oven = Oven("XXXX")
    # pass in any provided system arguments
    app = QApplication(sys.argv)
    main_window = MainWindow()

    set_temp_widget = SetTempWidget(oven)
    main_window.setCentralWidget(set_temp_widget)

    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
