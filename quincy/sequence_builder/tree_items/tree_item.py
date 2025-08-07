from __future__ import annotations

from abc import abstractmethod
from typing import Iterable, Protocol, Self, Sequence

from PyQt6.QtGui import QIcon

from ...utility.serde import Json


class TreeItem[SubItem: TreeItem](Protocol):
    """Interface representing items in a tree model."""

    @abstractmethod
    def serialize(self) -> Json:
        """Serialize the object into a JSON-like structure."""
        ...

    @abstractmethod
    def get_parent(self) -> TreeItem[Self] | None:
        """Get the item's parent, which is `None` if this is the root item."""
        ...

    @abstractmethod
    def set_parent(self, parent: TreeItem[Self] | None):
        """Set the item's parent."""
        ...

    def get_display_name(self) -> str:
        """Get the name displayed on the item."""
        return ""

    def get_icon(self) -> QIcon:
        """Get the icon displayed on the item."""
        return QIcon()

    def supports_subitems(self) -> bool:
        """Whether the item supports subitems."""
        return True

    def supports_dragging(self) -> bool:
        """Whether the item supports being dragged."""
        return False

    @abstractmethod
    def get_count(self) -> int:
        """Get the number of subitems."""
        ...

    def has_subitems(self) -> bool:
        """Whether this item contains subitems."""
        return self.get_count() > 0

    @abstractmethod
    def index(self, item: SubItem) -> int | None:
        """
        Try to find the index of **item** in this item's subitems. Returns `None` if **item** is not
        found.
        """
        ...

    def index_in_parent(self) -> int | None:
        """
        Try to find the index if this item in its parent. Returns `None` if this item is not a
        subitem of its parent.
        """
        ...
        parent = self.get_parent()
        if parent is None:
            return None
        return parent.index(self)

    @abstractmethod
    def get_subitem(self, index: int) -> SubItem | None:
        """Get the subitem at **index**."""
        ...

    def open_event(self) -> bool:
        """
        Handle the item being "opened" (i.e. double clicked).

        Returns
        -------
        Whether the item should be expanded in the model.
        """
        return True

    def expand_event(self):
        """Handle the item expanding."""
        return

    def collapse_event(self):
        """Handle the item collapsing."""
        return


class MutableTreeItem[SubItem: TreeItem](TreeItem):
    """`TreeItem` that can have subitems added/removed."""

    @abstractmethod
    def append_subitems(self, items: Iterable[SubItem]):
        """Append all **items** to this item's list of subitems."""
        ...

    @abstractmethod
    def insert_subitems(self, starting_row_index: int, items: Iterable[SubItem]):
        """
        Insert all **items** starting at **starting_row_index**, with the newest subitems on top.
        """
        ...

    @abstractmethod
    def remove_subitems(self, starting_row_index: int, count: int):
        """
        Remove **count** subitems starting at **starting_row_index**. Returns whether the operation
        succeeded.

        Raises
        ------
        IndexError
            **starting_row_index** or **count** are out of range.
        """
        ...


# --------------------------------------------------------------------------------------------------
# helper functions for external use
def index[SubItem: TreeItem](items: Sequence[SubItem], item: SubItem) -> int | None:
    """Helper function for `TreeItem.index()`."""
    try:
        return items.index(item)
    except ValueError:
        return None


def get_subitem[SubItem: TreeItem](items: Sequence[SubItem], index: int) -> SubItem | None:
    """Helper function for `TreeItem.get_subitem`."""
    try:
        return items[index]
    except IndexError:
        return None


def append_subitems[SubItem: TreeItem](
    parent: TreeItem[SubItem], items: list[SubItem], subitems: Iterable[SubItem]
):
    """Helper function for `TreeItem.append_subitem`. Appends all **items** to **subitems**."""
    for item in subitems:
        item.set_parent(parent)
    items.extend(subitems)


def insert_subitems[SubItem: TreeItem](
    parent: TreeItem[SubItem],
    items: list[SubItem],
    starting_row_index: int,
    subitems: Iterable[SubItem],
):
    """
    Helper function for `TreeItem.insert_subitems()`. Inserts all **items** into **subitems**,
    starting at **starting_row_index**.
    """
    for i, item in enumerate(subitems):
        item.set_parent(parent)
        items.insert(starting_row_index + i, item)


def remove_subitems[SubItem: TreeItem](items: list[SubItem], starting_row_index: int, count: int):
    """
    Helper function for `TreeItem.remove_subitems()`. Removes **count** items from **items**
    starting at **starting_row_index**.

    Raises
    ------
    IndexError
        **starting_row_index** or **count** are out of range.
    """
    del items[starting_row_index : starting_row_index + count]
