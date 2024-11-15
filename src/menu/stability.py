from PyQt6.QtWidgets import QMenu, QMenuBar
from PyQt6.QtCore import pyqtSignal
from actions import Action


class StabilityMenu(QMenu):
    """Stability check menu."""

    # signals
    statusChanged = pyqtSignal(bool)

    def __init__(self, parent: QMenuBar):
        super().__init__("S&tability", parent)
        self.create_actions(parent)

        self.addAction(self.cancel_stability_check)

    def create_actions(self, parent: QMenuBar):
        self.cancel_stability_check = Action(parent, "Cancel Stability Check")

    def handle_status_change(self, running: bool):
        self.cancel_stability_check.setEnabled(running)
