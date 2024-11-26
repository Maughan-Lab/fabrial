from PyQt6.QtWidgets import QMenu, QMenuBar
from PyQt6.QtCore import pyqtSignal
from actions import Action

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class ViewMenu(QMenu):
    """View menu."""

    poppedGraphDestroyed = pyqtSignal()

    def __init__(self, parent: QMenuBar, main_window: "MainWindow"):
        super().__init__("&View", parent)
        self.create_actions(parent, main_window)
        self.connect_signals()

        self.addAction(Action(parent, "Fullscreen", main_window.toggle_fullscreen, shortcut="F11"))
        self.addAction(
            Action(
                parent,
                "Shrink",
                main_window.shrink,
                shortcut="Ctrl+Shift+D",
            )
        )

        self.addSeparator()

        self.addAction(self.pop_graph)

    def create_actions(self, parent: QMenuBar, main_window: "MainWindow"):
        self.pop_graph = Action(
            parent,
            "Pop Sequence Graph",
            main_window.pop_graph,
            shortcut="Ctrl+G",
        )

    def connect_signals(self):
        self.pop_graph.triggered.connect(lambda: self.pop_graph.setEnabled(False))
        self.poppedGraphDestroyed.connect(lambda: self.pop_graph.setEnabled(True))
