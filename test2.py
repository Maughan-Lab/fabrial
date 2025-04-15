import sys
import time
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QThread, QReadLocker, QWriteLocker, QReadWriteLock
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class NestedWorker(QObject):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self.canceled = False
        self.paused = False
        self.mutex = QReadWriteLock()

    def run(self):
        for i in range(10):
            # this gets properly processed. Why?
            self.progress.emit(i)
            time.sleep(1)
            with QReadLocker(self.mutex):
                if self.canceled:
                    break
            while True:
                with QReadLocker(self.mutex):
                    if not self.paused:
                        break
                time.sleep(0.1)

        self.finished.emit()

    def cancel(self):
        # this never runs
        with QWriteLocker(self.mutex):
            self.canceled = True

    def pause(self):
        # this never runs
        with QWriteLocker(self.mutex):
            self.paused = True

    def unpause(self):
        # this never runs
        with QWriteLocker(self.mutex):
            self.paused = False


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    cancelCommand = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.nested_worker = NestedWorker(self)

        self.canceled = False
        self.paused = False

    def run(self):
        """Long-running task."""
        self.cancelCommand.connect(self.nested_worker.cancel, Qt.ConnectionType.DirectConnection)
        self.nested_worker.progress.connect(self.progress)
        self.nested_worker.finished.connect(self.finished)
        self.nested_worker.run()


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicksCount = 0
        self.setupUi()

    def setupUi(self):
        self.setWindowTitle("Freezing GUI")
        self.resize(300, 150)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # Create and connect widgets
        self.clicksLabel = QLabel("Counting: 0 clicks", self)
        self.clicksLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.stepLabel = QLabel("Long-Running Step: 0")
        self.stepLabel.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.countBtn = QPushButton("Click me!", self)
        self.countBtn.clicked.connect(self.countClicks)
        self.longRunningBtn = QPushButton("Long-Running Task!", self)
        self.longRunningBtn.clicked.connect(self.runLongTask)

        self.cancel_button = QPushButton("Cancel", self)
        self.pause_button = QPushButton("Pause", self)
        self.unpause_button = QPushButton("Unpause", self)
        # Set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.clicksLabel)
        layout.addWidget(self.countBtn)
        layout.addStretch()
        layout.addWidget(self.stepLabel)
        layout.addWidget(self.longRunningBtn)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.unpause_button)
        self.centralWidget.setLayout(layout)

    def countClicks(self):
        self.clicksCount += 1
        self.clicksLabel.setText(f"Counting: {self.clicksCount} clicks")

    def reportProgress(self, n):
        self.stepLabel.setText(f"Long-Running Step: {n}")

    def runLongTask(self):
        # Step 2: Create a QThread object
        self.threader = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.threader)
        # Step 5: Connect signals and slots
        self.threader.started.connect(self.worker.run)
        self.worker.finished.connect(self.threader.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.threader.finished.connect(self.threader.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # these three signals never get received
        self.cancel_button.pressed.connect(self.worker.cancelCommand, Qt.ConnectionType.DirectConnection)

        # Step 6: Start the thread
        self.threader.start()
        # Final resets
        self.longRunningBtn.setEnabled(False)
        self.threader.finished.connect(lambda: self.stepLabel.setText("Long-Running Step: 0"))


app = QApplication(sys.argv)
win = Window()
win.show()
sys.exit(app.exec())
