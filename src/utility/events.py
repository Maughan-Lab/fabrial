from PyQt6.QtCore import QCoreApplication, QEventLoop


def PROCESS_EVENTS():
    """Call `QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)`"""
    QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents, 10)
