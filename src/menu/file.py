from PyQt6.QtWidgets import QMenu, QMenuBar, QApplication
from ..classes.actions import Action
from ..custom_widgets.dialog import OkCancelDialog
from showinfm import show_in_file_manager  # TODO: find a better file manager solution
from os import path
import os
from .. import Files
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class FileMenu(QMenu):
    """File menu."""

    def __init__(self, parent: QMenuBar, main_window: "MainWindow"):
        super().__init__("&File", parent)
        # silly
        self.addAction(Action(parent, "Honk", lambda: OkCancelDialog("Honk", "Honk").exec()))

        self.addSeparator()

        self.addAction(Action(parent, "Show Data Files", self.show_data_files))

        self.addSeparator()

        self.addAction(Action(parent, "Close Window", main_window.close, shortcut="Alt+F4"))
        self.addAction(Action(parent, "Exit", QApplication.closeAllWindows))

    def show_data_files(self):
        if not path.exists(Files.Sequence.DATA_FOLDER):
            os.mkdir(Files.Sequence.DATA_FOLDER)
        show_in_file_manager(Files.Sequence.DATA_FOLDER, True)
