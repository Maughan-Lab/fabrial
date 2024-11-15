from PyQt6.QtWidgets import QMenu, QMenuBar
from actions import Action


class ViewMenu(QMenu):
    """View menu."""

    def __init__(self, parent: QMenuBar):
        super().__init__("&Edit", parent)

        self.addAction(Action(parent, "Fullscreen", lambda: print("NOT IMPLEMENTED")))
        self.addAction(Action(parent, "Shrink", lambda: print("NOT IMPLEMENTED")))

        self.addSeparator()

        self.addAction(Action(parent, "Pop Sequence Graph", lambda: print("NOT IMPLEMENTED")))
