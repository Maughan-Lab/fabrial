from PyQt6.QtCore import QCoreApplication, QEventLoop


def PROCESS_SIGNALS():
    """Call `QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)`"""
    QCoreApplication.processEvents(QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents)
