from PyQt6.QtWidgets import QMenu, QMenuBar
from actions import Action


class EditMenu(QMenu):
    """Edit menu."""

    def __init__(self, parent: QMenuBar):
        super().__init__("&Edit", parent)
        # TODO: implement these
        self.addAction(Action(parent, "Undo", lambda: print("NOT IMPLEMENTED")))
        self.addAction(Action(parent, "Redo", lambda: print("NOT IMPLEMENTED")))

        self.addSeparator()

        self.addAction(Action(parent, "Cut", lambda: print("NOT IMPLEMENTED")))
        self.addAction(Action(parent, "Copy", lambda: print("NOT IMPLEMENTED")))
        self.addAction(Action(parent, "Paste", lambda: print("NOT IMPLEMENTED")))
