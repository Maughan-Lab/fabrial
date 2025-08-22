from abc import abstractmethod
from collections.abc import Iterable
from typing import Protocol

from PyQt6.QtGui import QIcon

from ..classes import SequenceStep
from ..utility.serde import Deserialize, Serialize
from .item_widget import ItemWidget


class DataItem(Deserialize, Serialize, Protocol):
    """An inner item used by a `SequenceItem`."""

    # visuals
    @abstractmethod
    def display_name(self) -> str:
        """Get the name displayed on the item."""
        ...

    @abstractmethod
    def icon(self) -> QIcon:
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
        """Whether the item supports subitems. By default, items do not support subitems."""
        return False

    def expand_event(self):
        """Handle the item being expanded. Does nothing by default."""
        return

    def collapse_event(self):
        """Handle the item being collapsed. Does nothing by default."""
        return

    # sequence
    @abstractmethod
    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        """
        Create the `SequenceStep` this item represents.

        Parameters
        ----------
        substeps
            The `SequenceStep`s created from this item's subitems. For items that do not support
            subitems, this is always an empty iterable.

        Returns
        -------
        This item's `SequenceStep`.
        """
        ...


class WidgetDataItem(DataItem, Protocol):
    """A `DataItem` that uses an `ItemWidget` to display and modify data."""

    @abstractmethod
    def widget(self) -> ItemWidget:  # private
        """Get the widget this item uses."""
        ...

    def display_name(self) -> str:  # implementation
        return self.widget().windowTitle()

    def icon(self) -> QIcon:  # implementation
        return self.widget().windowIcon()

    def open_event(self, editable: bool):  # implementation
        self.widget().show_editable(editable)
