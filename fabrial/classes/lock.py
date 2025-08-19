from threading import RLock
from typing import Any


class DataLock[Data: Any]:
    def __init__(self, data: Data):
        self.lock = RLock()
        self.data = data

    def get(self) -> Data:
        """Get the inner data. Treat the returned value as immutable."""
        with self.lock:
            return self.data

    def set(self, data: Data):
        """Set the inner data to **data**."""
        with self.lock:
            self.data = data

    def __enter__(self) -> Data:
        self.lock.acquire()
        return self.data

    def __exit__(self, *args):  # we don't care about exceptions here
        self.lock.release()
