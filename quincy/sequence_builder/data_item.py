from abc import abstractmethod
from typing import Protocol

from PyQt6.QtGui import QIcon

from ..classes import Process
from ..utility.serde import Deserialize, Serialize


class DataItem(Deserialize, Serialize, Protocol):
    """An inner item used by a `TreeItem`."""

    # visuals
    @abstractmethod
    def get_display_name(self) -> str:
        """Get the name displayed on the item."""
        ...

    @abstractmethod
    def get_icon(self) -> QIcon:
        """Get the icon to display on the item."""
        ...

    @abstractmethod
    def open_event(self):
        """Handle the item being "opened" (i.e. double clicked)."""
        ...

    def supports_subitems(self) -> bool:
        """Whether the item supports subitems. By default, `Item`s do not support subitems."""
        return False

    def expand_event(self):
        """Handle the item being expanded. Does nothing by default."""
        return

    def collapse_event(self):
        """Handle the item being collapsed. Does nothing by default."""
        return

    # sequence
    @abstractmethod
    def create_process(self) -> Process:
        """Create the `Process` this item represents."""
        ...
