from PyQt6.QtCore import QCoreApplication, QEventLoop


def PROCESS_EVENTS():
    """Call `QCoreApplication.processEvents()` and let it run for 10ms."""
    QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents, 10)
