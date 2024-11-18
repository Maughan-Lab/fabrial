from PyQt6.QtWidgets import QMenuBar
from .file import FileMenu
from .view import ViewMenu
from .stability import StabilityMenu
from .sequence import SequenceMenu

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class MenuBar(QMenuBar):
    """The application's menubar."""

    def __init__(self, parent: "MainWindow"):
        super().__init__()
        self.create_submenus(parent)

    def create_submenus(self, parent: "MainWindow"):
        # need to store these because they have signals
        self.stability = StabilityMenu(self, parent.stability_check_widget)
        self.sequence = SequenceMenu(self, parent.sequence_widget)

        self.addMenu(FileMenu(self, parent))
        self.addMenu(ViewMenu(self, parent))
        self.addMenu(self.stability)
        self.addMenu(self.sequence)
