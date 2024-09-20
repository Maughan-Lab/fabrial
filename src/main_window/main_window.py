from PyQt6.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.setWindowTitle("Quincy")

# TODO: figure out how to structure this project, since
# you cannot have main_window.py and a folder called main_window