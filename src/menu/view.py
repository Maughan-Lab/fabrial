from PyQt6.QtWidgets import QMenu, QMenuBar, QMainWindow, QWidget, QVBoxLayout
from graph.widgets import GraphWidget
from actions import Action

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class ViewMenu(QMenu):
    """View menu."""

    def __init__(self, parent: QMenuBar, main_window: "MainWindow"):
        super().__init__("&View", parent)

        self.addAction(
            Action(
                parent, "Fullscreen", lambda: self.resize_main_window(main_window), shortcut="F11"
            )
        )
        self.addAction(Action(parent, "Shrink", lambda: self.shrink_main_window(main_window)))

        self.addSeparator()

        self.addAction(Action(parent, "Pop Sequence Graph", lambda: self.pop_graph(main_window)))

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
        return
        main_window.graph_widget.setHidden(not main_window.graph_widget.isHidden())
        self.second_window = QMainWindow()
        self.second_window.setCentralWidget(main_window.graph_widget)
        self.second_window.show()

# TODO: finish implementing the graph popping feature

class SecondaryWindow(QMainWindow):
    """Secondary window for holding popped graphs."""

    def __init__(self, graph: GraphWidget):
        super().__init__()
        self.graph = GraphWidget
        placeholder = QWidget()
        layout = QVBoxLayout()
        placeholder.setLayout(layout)
        layout.addWidget(self.graph)
        self.setCentralWidget(placeholder)
