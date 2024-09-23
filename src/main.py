# you may be wondering, "Why is there a folder called 'backend' where all of the actual source code
# is stored?" Well my friend, it is because Python has a horrendous import system. This was the only
# way for me to structure my project logically, so we are dealing with that now.

from backend.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
from backend.set_temperature.widgets import SetTempWidget

import sys


def main():
    # pass in any provided system arguments
    app = QApplication(sys.argv)
    main_window = MainWindow()

    set_temp_widget = SetTempWidget()
    main_window.setCentralWidget(set_temp_widget)

    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
