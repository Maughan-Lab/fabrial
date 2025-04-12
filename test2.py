import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)
from PyQt6.QtCore import Qt, QThreadPool, QRunnable, QObject, pyqtSignal
import time


class Signals(QObject):
    changeSignal = pyqtSignal(object)


class TestRunnable(QRunnable):
    def __init__(self, linked_widget: QLabel):
        super().__init__()
        self.signals = Signals()
        self.linked_widget = linked_widget

    def run(self):
        print("Start")
        time.sleep(1)
        self.linked_widget.setText("It also worked!!!!")
        time.sleep(3)
        print("End")


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        layout = QVBoxLayout()

        self.label1 = QLabel("Guy")
        self.label2 = QLabel("Girlie")
        button = QPushButton("Test")
        button.pressed.connect(self.test_func)

        layout.addWidget(self.label1)
        layout.addWidget(self.label2)
        layout.addWidget(button)

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.threadpool = QThreadPool(self)

    def test_func(self):
        runner = TestRunnable(self.label1)
        self.threadpool.start(runner)


app = QApplication(sys.argv)

window = MainWindow()
window.show()


app.exec()
