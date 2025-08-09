from dataclasses import dataclass, field

from PyQt6.QtCore import QMimeData


@dataclass
class Clipboard:
    clipboard_contents: QMimeData = field(default_factory=QMimeData)
    empty = True

    def set_contents(self, contents: QMimeData):
        """Set the clipboard contents."""
        self.clipboard_contents = contents
        self.empty = False

    def contents(self) -> QMimeData | None:
        """Get the clipboard contents. Returns None if the contents have not been set."""
        if self.empty:
            return None
        return self.clipboard_contents
