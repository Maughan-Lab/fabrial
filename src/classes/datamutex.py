from typing import TypeVar
from PyQt6.QtCore import QMutex, QMutexLocker
import time

Data = TypeVar("Data")


class DataMutex[Data](QMutex):  # generic class
    """Mutex with associated data."""

    def __init__(self, data: Data):
        super().__init__()
        self.data: Data = data

    def set(self, data: Data):
        """Set the data in this mutex, blocking until the mutex is available."""
        with QMutexLocker(self):
            self.data = data

    def try_set(self, data: Data):
        """
        Try to set the data in this mutex twice, calling **time.sleep()** in between. Returns True
        if successful, False otherwise. The caller MUST unlock the mutex.
        """
        for i in range(2):
            if self.tryLock():
                self.data = data
                return True
            if i != 1:
                time.sleep(0.01)
        return False

    def get(self) -> Data:
        """Get the data in this mutex, blocking until the mutex is available."""
        with QMutexLocker(self):
            return self.data

    def try_get(self) -> Data | None:
        """
        Try to set the data in this mutex twice, calling **time.sleep()** in between. Returns True
        if successful, False otherwise. The caller MUST unlock the mutex.
        """
        for i in range(2):
            if self.tryLock():
                return self.data
            if i != 1:
                time.sleep(0.01)
        return None
