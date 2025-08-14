from typing import Any, Callable

from PyQt6.QtCore import QCoreApplication, QEventLoop, QTimer


def PROCESS_EVENTS():
    """Call `QCoreApplication.processEvents()` and let it run for 10ms."""
    QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents, 10)


def delay_until_running(callback: Callable[[], Any]):
    """Queue a callback to run just after the application starts and the main window is shown."""
    QTimer.singleShot(0, callback)
