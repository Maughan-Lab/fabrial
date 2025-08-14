from typing import Iterable

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTabWidget, QWidget


class TabWidget(QTabWidget):
    """
    `QTabWidget` that creates the tabs in the constructor, looks better, and auto-focuses a tab
    when it is selected.

    Parameters
    ----------
    tabs
        Tuples of (widget to use for tab, tab name, tab icon).
    """

    def __init__(self, tabs: Iterable[tuple[QWidget, str, QIcon]]):
        QTabWidget.__init__(self)
        self.setDocumentMode(True)

        for tab, name, icon in tabs:
            self.addTab(tab, icon, name)

        self.currentChanged.connect(lambda index: self.widget(index).setFocus())  # type: ignore
