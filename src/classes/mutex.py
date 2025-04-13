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
from ..enums.status import SequenceStatus

Data = TypeVar("Data")


class MutexSignals(QObject):
    lockedChanged = pyqtSignal(bool)


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


class DataMutex[Data](QReadWriteLock):  # generic class
    """Mutex with associated data."""

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


class StatusStateMachine(DataMutex[SequenceStatus]):
    """
    Container for a SequenceStatus. This defines valid state transitions. If you try to set the
    state to an invalid state, it will be ignored.
    """

    def __init__(self, initial_status: SequenceStatus):
        """:param initial_status: The initial status to put in the mutex."""
        super().__init__(initial_status)

    def set(self, status: SequenceStatus) -> bool:
        """
        Set the internal status without emitting signals. Blocks until the mutex is available.

        :returns: True if the status changed (a valid state transition occurred), False otherwise.
        """
        match self.get():
            case SequenceStatus.INACTIVE | SequenceStatus.COMPLETED | SequenceStatus.CANCELED:
                # these can only go to ACTIVE
                match status:
                    case SequenceStatus.ACTIVE:
                        pass
                    case _:
                        return False
            case SequenceStatus.ACTIVE | SequenceStatus.PAUSED:
                # ACTIVE and PAUSED can go to any state
                pass
            case SequenceStatus.ERROR_PAUSED:
                # ERROR_PAUSED cannot go to PAUSED or ERROR
                match status:
                    case SequenceStatus.PAUSED | SequenceStatus.ERROR:
                        return False
            case SequenceStatus.ERROR:
                # ERROR cannot go to PAUSED
                match status:
                    case SequenceStatus.PAUSED:
                        return False
                    case _:
                        pass
        # if we made it here we are performing a valid state transition
        super().set(status)
        return True

    def try_set(self, data):
        """Do not call this method. It is a remnant from the base class."""
        raise Exception("ERROR: called try_set() on a StatusStateMachine.")

    def try_get(self):
        """Do not call this method. It is a remnant from the base class."""
        raise Exception("ERROR: called try_get() on a StatusStateMachine.")
