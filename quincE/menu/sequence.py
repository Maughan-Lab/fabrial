from PyQt6.QtWidgets import QMenu, QMenuBar

from ..classes import Action
from ..enums import SequenceStatus
from ..sequence_builder import SequenceTreeWidget


class SequenceMenu(QMenu):
    """Sequence menu."""

    def __init__(self, parent: QMenuBar, widget: SequenceTreeWidget):
        QMenu.__init__(self, "&Sequence", parent)
        self.skip: Action
        self.cancel: Action
        self.widget = widget

        self.create_actions(parent)
        self.connect_signals()

        # self.addAction(Action(parent, "Save Settings", widget.model.save_data, shortcut="Ctrl+S"))
        # self.addAction(self.load_settings)

        self.addSeparator()

        self.addAction(self.skip)
        self.addAction(self.cancel)

    def create_actions(self, parent: QMenuBar):
        # self.load_settings = Action(
        #     parent, "Load Settings", self.widget.model.load_data, shortcut="Ctrl+Shift+L"
        # )
        self.skip = Action(parent, "Skip Current Process", self.widget.command_signals.skipCommand)
        self.cancel = Action(parent, "Cancel Sequence", self.widget.command_signals.cancelCommand)
        # disable these initially
        for action in (self.skip, self.cancel):
            action.setDisabled(True)

    def connect_signals(self):
        """Connect external signals."""
        self.widget.sequenceStatusChanged.connect(self.update_action_states)

    def update_action_states(self, status: SequenceStatus):
        running = status.is_running()
        # self.load_settings.setEnabled(not running)
        self.skip.setEnabled(running)
        self.cancel.setEnabled(running)
