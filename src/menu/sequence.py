from PyQt6.QtWidgets import QMenu, QMenuBar
from actions import Action
from sequence.widgets import SequenceWidget


class SequenceMenu(QMenu):
    """Sequence menu."""

    def __init__(self, parent: QMenuBar, widget: SequenceWidget):
        super().__init__("&Sequence", parent)
        self.create_actions(parent, widget)
        self.connect_signals(widget)

        self.addAction(
            Action(parent, "Save Settings", lambda: print("NOT IMPLEMENTED"), shortcut="Ctrl+S")
        )
        self.addAction(self.load_settings)

        self.addSeparator()

        self.addAction(
            Action(
                parent, "Generate Graph", lambda: print("NOT IMPLEMENTED"), shortcut="Ctrl+Shift+G"
            )
        )

        self.addSeparator()

        self.addAction(self.skip_current_cycle)
        self.addAction(self.skip_current_buffer)
        self.addAction(self.cancel_sequence)

    def create_actions(self, parent: QMenuBar, widget: SequenceWidget):
        self.load_settings = Action(
            parent, "Load Settings", self.load_saved_settings, shortcut="Ctrl+Shift+L"
        )
        self.skip_current_cycle = Action(parent, "Skip Current Cycle", widget.skipCycle.emit)
        self.skip_current_buffer = Action(parent, "Skip Current Buffer", widget.skipBuffer.emit)
        self.cancel_sequence = Action(parent, "Cancel Sequence", widget.cancelSequence.emit)
        # disable these initially
        for action in (self.skip_current_cycle, self.skip_current_buffer, self.cancel_sequence):
            action.setEnabled(False)

    def connect_actions(self):
        """Connect internal action signals."""
        # disable skipping until the cycle/buffer has been officially skipped
        self.skip_current_cycle.triggered.connect(lambda: self.skip_current_cycle.setEnabled(False))
        self.skip_current_buffer.triggered.connect(
            lambda: self.skip_current_buffer.setEnabled(False)
        )

    def connect_signals(self, widget: SequenceWidget):
        """Connect external signals."""
        widget.cycleSkipped.connect(lambda: self.skip_current_cycle.setEnabled(True))
        widget.bufferSkipped.connect(lambda: self.skip_current_buffer.setEnabled(True))
        widget.statusChanged.connect(self.handle_status_change)

    def handle_status_change(self, running: bool):
        self.load_settings.setEnabled(running)
        self.cancel_sequence.setEnabled(running)
        self.skip_current_cycle.setEnabled(running)
        self.skip_current_buffer.setEnabled(running)

    def load_saved_settings(self):
        print("NOT IMPLEMENTED")
        pass
