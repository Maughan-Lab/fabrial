from abc import abstractmethod
from typing import Protocol, Self, runtime_checkable

from PyQt6.QtGui import QIcon

from ..classes import Process
from ..utility.serde import Deserialize, Serialize
from .item_widget import ItemWidget


@runtime_checkable
class DataItem(Deserialize, Serialize, Protocol):
    """An inner item used by a `TreeItem`."""

    @classmethod
    @abstractmethod
    def default(cls) -> Self:
        """Create the item with default parameters."""
        ...

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
    def open_event(self, editable: bool):
        """
        Handle the item being "opened" (i.e. double clicked).

        Parameters
        ----------
        editable
            Whether the item's data should be editable.
        """
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


class WidgetDataItem(DataItem, Protocol):
    """A `DataItem` that uses an `ItemWidget` to display and modify data."""

    @abstractmethod
    def get_widget(self) -> ItemWidget:  # private
        """Get the widget this item uses."""
        ...

    def get_display_name(self) -> str:  # implementation
        return self.get_widget().windowTitle()

    def get_icon(self) -> QIcon:  # implementation
        return self.get_widget().windowIcon()

    def open_event(self, editable: bool):  # implementation
        self.get_widget().show_editable(editable)
