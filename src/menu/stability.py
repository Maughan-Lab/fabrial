from PyQt6.QtWidgets import QMenu, QMenuBar
from actions import Action
from stability_check.widgets import StabilityCheckWidget


class StabilityMenu(QMenu):
    """Stability check menu."""

    def __init__(self, parent: QMenuBar, widget: StabilityCheckWidget):
        super().__init__("S&tability", parent)
        self.create_actions(parent, widget)
        self.connect_signals(widget)

        self.addAction(self.cancel_stability_check)

    def create_actions(self, parent: QMenuBar, widget: StabilityCheckWidget):
        self.cancel_stability_check = Action(
            parent, "Cancel Stability Check", widget.cancelStabilityCheck.emit
        )
        self.cancel_stability_check.setEnabled(False)

    def connect_signals(self, widget: StabilityCheckWidget):
        widget.statusChanged.connect(self.handle_status_change)

    def handle_status_change(self, running: bool):
        self.cancel_stability_check.setEnabled(running)
