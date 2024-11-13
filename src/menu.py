from PyQt6.QtWidgets import QMenuBar, QMenu, QApplication
from actions import Action
from custom_widgets.dialog import OkCancelDialog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class MenuBar(QMenuBar):
    """The application's menubar."""

    def __init__(self, parent: "MainWindow"):
        super().__init__()
        self.create_file(parent)

    def create_file(self, parent: "MainWindow"):
        file: QMenu = self.addMenu("&File")
        file.addAction(
            Action(parent, "Honk", lambda: OkCancelDialog("Honk", "Honk").exec())
        )  # silly

        file.addSeparator()
        # TODO: implement this
        file.addAction(Action(parent, "Show Data Files", lambda: print("NOT IMPLEMENTED")))

        file.addSeparator()

        file.addAction(Action(parent, "Close Window", parent.close))
        file.addAction(Action(parent, "Exit", QApplication.closeAllWindows))

    def create_edit(self):
        pass

    def create_view(self):
        pass

    def create_stability(self):
        pass

    def create_sequence(self):
        pass
