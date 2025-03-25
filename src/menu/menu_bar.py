from PyQt6.QtWidgets import QMenuBar
from .file import FileMenu
from .view import ViewMenu
from .stability import StabilityMenu
from .sequence import SequenceMenu
from instruments import InstrumentSet  # ../instruments.py

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class MenuBar(QMenuBar):
    """The application's menubar."""

    def __init__(self, parent: "MainWindow", instruments: InstrumentSet):
        super().__init__()
        self.create_submenus(parent, instruments)

    def create_submenus(self, parent: "MainWindow", instruments: InstrumentSet):
        # need to store these because they have signals
        self.stability = StabilityMenu(self, parent.oven_control_tab.stability_check_widget)
        self.sequence = SequenceMenu(
            self, parent.oven_control_tab.sequence_widget, parent, instruments
        )
        self.view = ViewMenu(self, parent)

        self.addMenu(FileMenu(self, parent))
        self.addMenu(self.view)
        self.addMenu(self.stability)
        self.addMenu(self.sequence)
