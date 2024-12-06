from PyQt6.QtCore import QObject, QMutex, pyqtSignal


class SignalMutex(QMutex):
    """**QMutex** with a signal indicating the lock status changed."""

    def __init__(self):
        super().__init__()
        self.signals = MutexSignals()
        self.lockChanged = self.signals.lockedChanged

    def lock(self):
        """Lock the mutex (emits a signal)."""
        super().lock()
        self.lockChanged.emit(False)

    def unlock(self):
        """Unlock the lock (emits a signal)."""
        self.lockChanged.emit(True)
        super().unlock()

    def unlock_silent(self):
        """Unlock without emitting a signal (usually used with tryLock())."""
        super().unlock()


class MutexSignals(QObject):
    lockedChanged = pyqtSignal(bool)
