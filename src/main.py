from main_window.main_window import MainWindow
from PyQt6.QtWidgets import QApplication
import sys


def main():
    # pass in any provided system arguments
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec()


if __name__ == "__main__":
    main()
