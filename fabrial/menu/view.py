from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QMenu, QMenuBar

from ..classes import Action

if TYPE_CHECKING:
    from ..main_window import MainWindow


class ViewMenu(QMenu):
    """View menu."""

    def __init__(self, parent: QMenuBar, main_window: MainWindow):
        self.pop_graph: Action

        QMenu.__init__(self, "&View", parent)

        self.addAction(
            Action(main_window, "Fullscreen", main_window.toggle_fullscreen, shortcut="F11")
        )
        self.addAction(
            Action(
                main_window,
                "Shrink",
                main_window.shrink,
                shortcut="Ctrl+Shift+D",
            )
        )
