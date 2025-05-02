import sys

from PyQt6.QtWidgets import QApplication, QMainWindow

# print(platform.system())
app = QApplication(sys.argv)
window = QMainWindow()
window.show()
app.exec()
