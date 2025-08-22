from __future__ import annotations

from abc import abstractmethod
from collections.abc import Iterable, MutableSequence, Sequence
from typing import Protocol

from PyQt6.QtGui import QIcon

from ...utility.serde import Json


class TreeItem(Protocol):
    """Interface representing items in a tree model."""

    @abstractmethod
    def serialize(self) -> Json:
        """Serialize the object into a JSON-like structure."""
        ...

    @abstractmethod
    def parent(self) -> TreeItem | None:
        """Get the item's parent, which is `None` if this is the root item."""
        ...

    @abstractmethod
    def set_parent(self, parent: TreeItem | None):
        """Set the item's parent."""
        ...

    def display_name(self) -> str:
        """Get the name displayed on the item."""
        return ""

    def icon(self) -> QIcon:
        """Get the icon displayed on the item."""
        return QIcon()

    def supports_subitems(self) -> bool:
        """Whether the item supports subitems."""
        return True

    def supports_dragging(self) -> bool:
        """Whether the item supports being dragged."""
        return False

    @abstractmethod
    def subitem_count(self) -> int:
        """Get the number of subitems."""
        ...

    def has_subitems(self) -> bool:
        """Whether this item contains subitems."""
        return self.subitem_count() > 0

    @abstractmethod
    def index(self, item: TreeItem) -> int | None:
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
        parent = self.parent()
        if parent is None:
            return None
        return parent.index(self)

    @abstractmethod
    def get_subitem(self, index: int) -> TreeItem | None:
        """Get the subitem at **index**."""
        ...

    def open_event(self, editable: bool) -> bool:
        """
        Handle the item being "opened" (i.e. double clicked).

        Parameters
        ----------
        editable
            Whether the item should be editable.

        Returns
        -------
        Whether the item's expansion state should be toggled.
        """
        return True

    def expand_event(self):
        """Handle the item expanding."""
        return

    def collapse_event(self):
        """Handle the item collapsing."""
        return


class GenericTreeItem[SubItem: TreeItem](TreeItem):
    """`TreeItem` with a known subitem type."""

    @abstractmethod
    def get_subitem(self, index: int) -> SubItem | None:  # overridden for typing
        ...


class MutableTreeItem[SubItem: TreeItem](GenericTreeItem[SubItem]):
    """`GenericTreeItem` with support for adding/removing subitems."""

    @abstractmethod
    def append_subitems(self, items: Iterable[SubItem]):
        """Append all **items** to this item's list of subitems."""
        ...

    @abstractmethod
    def insert_subitems(self, start: int, items: Iterable[SubItem]):
        """Insert all **items**, starting at **start**, with the newest subitems on top."""
        ...

    @abstractmethod
    def remove_subitems(self, start: int, count: int):
        """Remove **count** subitems starting at **start**."""
        ...


# --------------------------------------------------------------------------------------------------
# helper functions for external use
def index[SubItem: TreeItem](items: Sequence[SubItem], item: SubItem) -> int | None:
    """Helper function for `TreeItem.index()`. Linear searches for **item** by memory address."""
    # we don't use `Sequence.index()` here because if `SubItem` implements `__eq__()` we might
    # find the wrong item. We need to specifically compare by memory address, not value
    for i, subitem in enumerate(items):
        if subitem is item:
            return i
    return None


def get_subitem[SubItem: TreeItem](items: Sequence[SubItem], index: int) -> SubItem | None:
    """Helper function for `TreeItem.get_subitem`."""
    try:
        return items[index]
    except IndexError:
        return None


def append_subitems[SubItem: TreeItem](
    parent: MutableTreeItem[SubItem], items: MutableSequence[SubItem], subitems: Iterable[SubItem]
):
    """Helper function for `TreeItem.append_subitem`. Appends all **items** to **subitems**."""
    for item in subitems:
        item.set_parent(parent)
    items.extend(subitems)


def insert_subitems[SubItem: TreeItem](
    parent: MutableTreeItem[SubItem],
    items: MutableSequence[SubItem],
    start: int,
    subitems: Iterable[SubItem],
):
    """
    Helper function for `TreeItem.insert_subitems()`. Inserts all **items** into **subitems**,
    starting at **start**.
    """
    for i, item in enumerate(subitems):
        item.set_parent(parent)
        items.insert(start + i, item)


def remove_subitems[SubItem: TreeItem](items: MutableSequence[SubItem], start: int, count: int):
    """
    Helper function for `TreeItem.remove_subitems()`. Removes **count** items from **items**
    starting at **start**.
    """
    del items[start : start + count]
