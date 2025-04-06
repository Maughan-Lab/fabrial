from PyQt6.QtCore import QMimeData
from dataclasses import dataclass


@dataclass
class SequenceClipboard:
    clipboard_contents: QMimeData = QMimeData()
    empty = True

    def set_contents(self, contents: QMimeData):
        self.clipboard_contents = contents
        self.empty = False

    def contents(self) -> QMimeData:
        return self.clipboard_contents


# this variable can be accessed by any TreeView/TreeModel
CLIPBOARD = SequenceClipboard()
