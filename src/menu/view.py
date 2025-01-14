from PyQt6.QtWidgets import QMenu, QMenuBar
from PyQt6.QtCore import pyqtSignal
from actions import Action

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class ViewMenu(QMenu):
    """View menu."""

    def __init__(self, parent: QMenuBar, main_window: "MainWindow"):
        super().__init__("&View", parent)
        self.create_actions(parent)
        self.connect_signals(main_window)

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

    def create_actions(self, parent: QMenuBar):
        self.pop_graph = Action(
            parent,
            "Pop Sequence Graph",
            shortcut="Ctrl+G",
        )
        self.pop_graph.setCheckable(True)

    def connect_signals(self, main_window: "MainWindow"):
        """Connect action signals."""
        self.pop_graph.triggered.connect(
            lambda is_checked: main_window.pop_graph() if is_checked else main_window.unpop_graph()
        )

    def handle_popped_graph_destruction(self):
        """Uncheck the Pop Graph option without triggering signals."""
        self.pop_graph.blockSignals(True)
        self.pop_graph.setChecked(False)
        self.pop_graph.blockSignals(False)
