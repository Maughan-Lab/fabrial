from PyQt6.QtWidgets import QMenu, QMenuBar
from actions import Action
from graph.widgets import PoppedGraph  # ../graph

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class ViewMenu(QMenu):
    """View menu."""

    def __init__(self, parent: QMenuBar, main_window: "MainWindow"):
        super().__init__("&View", parent)
        self.create_actions(parent, main_window)

        self.addAction(
            Action(
                parent, "Fullscreen", lambda: self.resize_main_window(main_window), shortcut="F11"
            )
        )
        self.addAction(
            Action(
                parent,
                "Shrink",
                lambda: self.shrink_main_window(main_window),
                "Shrink the window to its smallest size.",
                "Ctrl+Shift+D",
            )
        )

        self.addSeparator()

        self.addAction(self.pop)

    def create_actions(self, parent: QMenuBar, main_window: "MainWindow"):
        self.pop = Action(
            parent,
            "Pop Sequence Graph",
            lambda: self.pop_graph(main_window),
            "Move the graph to a new window.",
            "Ctrl+G",
        )

    def resize_main_window(self, main_window: "MainWindow"):
        if main_window.isFullScreen():
            main_window.showNormal()
        else:
            main_window.showFullScreen()

    def shrink_main_window(self, main_window: "MainWindow"):
        if main_window.isFullScreen():
            main_window.showNormal()
        main_window.resize(main_window.minimumSize())

    def pop_graph(self, main_window: "MainWindow"):
        self.pop.setEnabled(False)
        popped_graph = PoppedGraph(main_window.graph_widget)
        popped_graph.destroyed.connect(lambda: self.pop.setEnabled(True))
        main_window.new_window(popped_graph)


# TODO: finish implementing the graph popping feature
