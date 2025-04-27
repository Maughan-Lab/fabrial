from PyQt6.QtWidgets import QMenuBar
from ..classes.actions import Action
from .file import FileMenu
from .view import ViewMenu
from .sequence import SequenceMenu
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..main_window import MainWindow


class MenuBar(QMenuBar):
    """The application's menubar."""

    def __init__(self, main_window: "MainWindow"):
        super().__init__()
        self.create_submenus(main_window)

    def create_submenus(self, main_window: "MainWindow"):
        # need to store these because they have signals
        self.sequence = SequenceMenu(self, main_window.sequence_tab.sequence_tree)
        self.view = ViewMenu(self, main_window, main_window.sequence_visuals_tab)

        self.addMenu(FileMenu(self, main_window))
        self.addMenu(self.view)
        self.addMenu(self.sequence)
        # TODO: implement settings thing
        self.addAction(Action(self, "Settings", self.temp))

    def temp(self):
        x = [1, 2]
        x[3]
