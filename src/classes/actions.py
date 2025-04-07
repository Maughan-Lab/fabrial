from PyQt6.QtCore import QObject, Qt
from PyQt6.QtGui import QAction, QKeySequence, QShortcut
from typing import Callable, Any


class Action(QAction):
    """Easy QAction class."""

    def __init__(
        self,
        parent: QObject,
        name: str,
        action: Callable[..., Any] | None = None,
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


class Shortcut(QShortcut):
    """Easy QShortcut class."""

    def __init__(
        self,
        parent: QObject,
        key: str,
        *actions: Callable[[], Any],
        context: Qt.ShortcutContext = Qt.ShortcutContext.WindowShortcut
    ):
        """
        Creates a QShortcut tied to **parent**.

        :param parent: The QObject to tie this shortcut to.
        :param key: A keyboard shortcut in the form of "Ctrl+A".
        :param *actions: The function(s) this shortcut executes.
        """
        super().__init__(QKeySequence(key), parent, context=context)
        for action in actions:
            self.activated.connect(action)
