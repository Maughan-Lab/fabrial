from collections.abc import Callable
from typing import Any

from PyQt6.QtCore import QObject, Qt, pyqtBoundSignal
from PyQt6.QtGui import QAction, QKeySequence, QShortcut


class Action(QAction):
    """
    Easy QAction class.

    Parameters
    ----------
    parent
        The QObject to tie this action to.
    name
        The displayed name of this action in a QMenuBar.
    actions
        The function(s) this action calls.
    status_tip
        Optional text that is shown when a user hovers over the action.
    shortcut
        An optional keyboard shortcut in the form of "Ctrl+A".
    shortcut_context
        The shortcut context. Defaults to `Qt.ShortcutContext.WindowShortcut`.
    """

    def __init__(
        self,
        parent: QObject,
        name: str,
        *actions: Callable[..., Any] | pyqtBoundSignal,
        status_tip: str | None = None,
        shortcut: str | None = None,
        shortcut_context: Qt.ShortcutContext = Qt.ShortcutContext.WindowShortcut,
    ):
        QAction.__init__(self, name, parent)
        for action in actions:
            self.triggered.connect(action)
        self.setStatusTip(status_tip)
        if shortcut is not None:
            self.setShortcut(QKeySequence(shortcut))
            self.setShortcutContext(shortcut_context)


class Shortcut(QShortcut):
    """
    Easy QShortcut class.

    Parameters
    ----------
    parent
        The QObject to tie this shortcut to.
    key
        A keyboard shortcut in the form of "Ctrl+A".
    actions
        The function(s) this shortcut executes.
    context
        The shortcut context. Default `WindowShortcut`.
    """

    def __init__(
        self,
        parent: QObject,
        key: str,
        *actions: Callable[[], Any],
        context: Qt.ShortcutContext = Qt.ShortcutContext.WindowShortcut,
    ):
        QShortcut.__init__(self, QKeySequence(key), parent, context=context)
        for action in actions:
            self.activated.connect(action)
