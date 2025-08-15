from typing import Any

from PyQt6.QtCore import QReadLocker, QReadWriteLock, QWriteLocker


class DataMutex[Data: Any](QReadWriteLock):  # generic class
    """QReadWriteMutex with associated data."""

    def __init__(self, data: Data):
        QReadWriteLock.__init__(self)
        self.data: Data = data

    def set(self, data: Data):
        """Set the data in this mutex, blocking until the mutex is available."""
        with QWriteLocker(self):
            self.data = data

    def try_set(self, data: Data):
        """
        Try to set the data in this mutex. Returns True if successful, False otherwise.
        """
        if self.tryLockForWrite(10):  # arbitrary time
            self.data = data
            self.unlock()
            return True
        return False

    def get(self) -> Data:
        """Get the data in this mutex, blocking until the mutex is available."""
        with QReadLocker(self):
            return self.data

    def try_get(self) -> Data | None:
        """
        Try to set the data in this mutex twice, calling `time.sleep()` in between. Returns True
        if successful, False otherwise.
        """
        if self.tryLockForRead(10):  # arbitrary time
            data = self.data
            self.unlock()
            return data
        return None
