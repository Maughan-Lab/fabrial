from PyQt6.QtWidgets import QMenu, QMenuBar, QApplication
from sequence.constants import DATA_FILES_LOCATION  # ../sequence
from actions import Action
from custom_widgets.dialog import OkCancelDialog
from showinfm import show_in_file_manager  # TODO: find a better file manager solution
from os import path
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class FileMenu(QMenu):
    """File menu."""

    def __init__(self, parent: QMenuBar, main_window: "MainWindow"):
        super().__init__("&File", parent)
        self.addAction(
            Action(parent, "Honk", lambda: OkCancelDialog("Honk", "Honk").exec())
        )  # silly

        self.addSeparator()
        # TODO: implement this
        self.addAction(Action(parent, "Show Data Files", self.show_data_files))

        self.addSeparator()

        self.addAction(Action(parent, "Close Window", main_window.close, shortcut="Alt+F4"))
        self.addAction(Action(parent, "Exit", QApplication.closeAllWindows))

    def show_data_files(self):
        if not path.exists(DATA_FILES_LOCATION):
            os.mkdir(DATA_FILES_LOCATION)
        show_in_file_manager(DATA_FILES_LOCATION, True)
