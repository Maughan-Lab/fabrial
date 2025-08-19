from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenuBar

from ..classes import Action
from .file import FileMenu
from .sequence import SequenceMenu
from .view import ViewMenu

if TYPE_CHECKING:
    from ..main_window import MainWindow


class MenuBar(QMenuBar):
    """The application's menubar."""

    def __init__(self, main_window: "MainWindow"):
        QMenuBar.__init__(self)
        self.create_submenus(main_window)

    def create_submenus(self, main_window: "MainWindow"):
        # need to store these because they have signals
        self.sequence = SequenceMenu(self)
        self.view = ViewMenu(self, main_window)
        self.addMenu(FileMenu(self, main_window))
        self.addMenu(self.view)
        self.addMenu(self.sequence)

        self.right_menu_bar = QMenuBar(self)
        self.setCornerWidget(self.right_menu_bar, Qt.Corner.TopRightCorner)
        self.right_menu_bar.addAction(Action(self, "Settings", main_window.show_settings))
