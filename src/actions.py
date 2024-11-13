from PyQt6.QtCore import QObject
from PyQt6.QtGui import QAction, QKeySequence
from typing import Callable, Any


class Action(QAction):
    """Easy QAction class."""

    def __init__(
        self,
        parent: QObject,
        name: str,
        action: Callable[[], Any],
        status_tip: str | None = None,
        shortcut: QKeySequence | None = None,
    ):
        super().__init__(name, parent)
        self.triggered.connect(action)
        self.setStatusTip(status_tip)
        if shortcut is not None:
            self.setShortcut(shortcut)
