from __future__ import annotations

from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QApplication, QMenu, QMenuBar

from ..classes import Action
from ..custom_widgets import OkCancelDialog

if TYPE_CHECKING:
    from ..main_window import MainWindow


class FileMenu(QMenu):
    """File menu."""

    def __init__(self, parent: QMenuBar, main_window: MainWindow):
        QMenu.__init__(self, "&File", parent)
        # silly
        self.addAction(Action(parent, "Honk", lambda: OkCancelDialog("Honk", "Honk").exec()))

        self.addSeparator()

        self.addAction(Action(parent, "Close Window", main_window.close, shortcut="Alt+F4"))
        self.addAction(Action(parent, "Exit", QApplication.closeAllWindows))
