from PyQt6.QtCore import QObject, QMutex, pyqtSignal


class SignalMutex(QMutex):
    """**QMutex** with a signal indicating the lock status changed."""

    def __init__(self):
        super().__init__()
        self.signals = MutexSignals()
        self.lockChanged = self.signals.lockedChanged

    def lock(self):
        super().lock()
        self.lockChanged.emit(False)

    def unlock(self):
        self.lockChanged.emit(True)
        super().unlock()


class MutexSignals(QObject):
    lockedChanged = pyqtSignal(bool)
