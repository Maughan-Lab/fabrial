from typing import Any, Callable

from PyQt6.QtCore import QTimer


def delay_until_running(callback: Callable[[], Any]):
    """Queue a callback for the next run of the event loop."""
    QTimer.singleShot(0, callback)
