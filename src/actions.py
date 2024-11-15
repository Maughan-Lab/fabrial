from PyQt6.QtCore import QObject
from PyQt6.QtGui import QAction, QKeySequence
from typing import Callable, Any


class Action(QAction):
    """Easy QAction class."""

    def __init__(
        self,
        parent: QObject,
        name: str,
        action: Callable[[], Any] | None = None,
        status_tip: str | None = None,
        shortcut: str | None = None,
    ):
        """
        Creates a QAction tied to **parent**.

        :param parent: The QObject to tie this action to.
        :param name: The displayed name of this action in a QMenuBar.
        :param action: The function this action calls.
        :param status_tip: Optional text that is shown when a user hovers over the action.
        :param shortcut: An optional keyboard shortcut in the form of "Ctrl+A".
        """
        super().__init__(name, parent)
        if action is not None:
            self.triggered.connect(action)
        self.setStatusTip(status_tip)
        if shortcut is not None:
            self.setShortcut(QKeySequence(shortcut))
