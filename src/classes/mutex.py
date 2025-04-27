from PyQt6.QtCore import (
    QObject,
    QMutex,
    pyqtSignal,
    QReadWriteLock,
    QWriteLocker,
    QReadLocker,
)
import time
from typing import TypeVar

Data = TypeVar("Data")


class MutexSignals(QObject):
    lockedChanged = pyqtSignal(bool)


class SignalMutex(QMutex):
    """**QMutex** with a signal indicating the lock status changed."""

    def __init__(self):
        super().__init__()
        self.signals = MutexSignals()
        self.lockChanged = self.signals.lockedChanged  # shortcut

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


class DataMutex[Data](QReadWriteLock):  # generic class
    """QReadWriteMutex with associated data."""

    def __init__(self, data: Data):
        super().__init__()
        self.data: Data = data

    def set(self, data: Data):
        """Set the data in this mutex, blocking until the mutex is available."""
        with QWriteLocker(self):
            self.data = data

    def try_set(self, data: Data):
        """
        Try to set the data in this mutex twice, calling **time.sleep()** in between. Returns True
        if successful, False otherwise.
        """
        for i in range(2):
            if self.tryLockForWrite():
                self.data = data
                self.unlock()
                return True
            if i != 1:
                time.sleep(0.01)
        return False

    def get(self) -> Data:
        """Get the data in this mutex, blocking until the mutex is available."""
        with QReadLocker(self):
            return self.data

    def try_get(self) -> Data | None:
        """
        Try to set the data in this mutex twice, calling **time.sleep()** in between. Returns True
        if successful, False otherwise.
        """
        for i in range(2):
            if self.tryLockForRead():
                data = self.data
                self.unlock()
                return data
            if i != 1:
                time.sleep(0.01)
        return None
