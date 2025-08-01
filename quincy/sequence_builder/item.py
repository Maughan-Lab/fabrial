from typing import Protocol
from abc import abstractmethod
from PyQt6.QtGui import QIcon
from ..utility.serde import Deserialize, Serialize


class Item(Protocol, Deserialize, Serialize):
    """An inner item used by a `TreeItem`."""

    SUPPORTS_SUBITEMS: bool

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

    def expand_event(self):
        """Handle the item being expanded."""
        pass

    def collapse_event(self):
        """Handle the item being collapsed."""
        pass

    # sequence
    def create_process(self) -> None:  # TODO: Process class
        """Create the `Process` this item represents."""
        ...
