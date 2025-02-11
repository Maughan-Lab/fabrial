from PyQt6.QtWidgets import QMainWindow
from .widgets import EISOptionsWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gamry-Side")
        widget = EISOptionsWidget()
        self.setCentralWidget(widget)
