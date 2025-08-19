from PyQt6.QtWidgets import QMenu, QMenuBar

from ..classes import Action


class SequenceMenu(QMenu):
    """Sequence menu."""

    def __init__(self, parent: QMenuBar):
        QMenu.__init__(self, "&Sequence", parent)
        self.cancel = Action(parent, "Cancel Sequence")
        self.cancel.setDisabled(True)  # start disabled
        self.addAction(self.cancel)
