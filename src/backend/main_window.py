from PyQt6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("Quincy")
