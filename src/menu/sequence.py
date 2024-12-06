from PyQt6.QtWidgets import QMenu, QMenuBar
from actions import Action  # ../actions.py
from sequence.widgets import SequenceWidget  # ../sequence
from enums.status import StabilityStatus  # ../enums
from instruments import InstrumentSet  # ../instruments.py


class SequenceMenu(QMenu):
    """Sequence menu."""

    def __init__(self, parent: QMenuBar, widget: SequenceWidget, instruments: InstrumentSet):
        super().__init__("&Sequence", parent)
        self.oven = instruments.oven
        self.widget = widget

        self.create_actions(parent)
        self.connect_signals()

        self.addAction(Action(parent, "Save Settings", widget.model.save_data, shortcut="Ctrl+S"))
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

    def create_actions(self, parent: QMenuBar):
        self.load_settings = Action(
            parent, "Load Settings", self.widget.model.load_data, shortcut="Ctrl+Shift+L"
        )
        self.skip_current_cycle = Action(parent, "Skip Current Cycle", self.widget.skipCycle.emit)
        self.skip_current_buffer = Action(
            parent, "Skip Current Buffer", self.widget.skipBuffer.emit
        )
        self.cancel_sequence = Action(parent, "Cancel Sequence", self.widget.cancelSequence.emit)
        # disable these initially
        for action in (self.skip_current_cycle, self.skip_current_buffer, self.cancel_sequence):
            action.setEnabled(False)

    def connect_signals(self):
        """Connect external signals."""
        self.widget.statusChanged.connect(
            lambda running: self.update_action_states(running, self.oven.is_connected())
        )
        self.widget.stabilityChanged.connect(self.handle_stability_change)
        self.oven.connectionChanged.connect(
            lambda connected: self.update_action_states(self.widget.is_running(), connected)
        )

    def update_action_states(self, running: bool, connected: bool):
        self.load_settings.setEnabled(not running)
        self.cancel_sequence.setEnabled(running)
        self.skip_current_cycle.setEnabled(running and connected)
        if not running or not connected:
            self.skip_current_buffer.setEnabled(False)

    def handle_stability_change(self, status: StabilityStatus):
        match status:
            case StabilityStatus.BUFFERING:
                enabled = True
            case _:
                enabled = False
        self.skip_current_buffer.setEnabled(enabled)
