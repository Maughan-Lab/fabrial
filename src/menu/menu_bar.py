from PyQt6.QtWidgets import QMenuBar
from .file import FileMenu
from .view import ViewMenu
from .stability import StabilityMenu
from .old_sequence import OldSequenceMenu
from .sequence import SequenceMenu
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..main_window import MainWindow


class MenuBar(QMenuBar):
    """The application's menubar."""

    def __init__(self, parent: "MainWindow"):
        super().__init__()
        self.create_submenus(parent)

    def create_submenus(self, parent: "MainWindow"):
        # need to store these because they have signals
        self.stability = StabilityMenu(self, parent.oven_control_tab.stability_check_widget)
        self.old_sequence = OldSequenceMenu(self, parent.oven_control_tab.sequence_widget, parent)
        self.sequence = SequenceMenu(self, parent.sequence_tab.sequence_tree)
        self.view = ViewMenu(self, parent)

        self.addMenu(FileMenu(self, parent))
        self.addMenu(self.view)
        self.addMenu(self.stability)
        self.addMenu(self.old_sequence)
        self.addMenu(self.sequence)
