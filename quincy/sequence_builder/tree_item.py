from __future__ import annotations

from abc import abstractmethod
from typing import Any, Protocol, Self, Sequence

from PyQt6.QtGui import QIcon

from ..utility import images, serde
from .item import Item

TYPE = "type"
WIDGET_DATA = "linked-widget-data"
SUBITEMS = "subitems"
ITEM = "item"

DEFAULT_ICON_FILENAME = "script.png"


class TreeItem[SubItemType: "TreeItem"](Protocol):
    """Abstract class to represent items in a `TreeModel`."""

    SUPPORTS_DRAGGING: bool

    @abstractmethod
    def get_parent(self) -> TreeItem | None:
        """Get the item's parent, which is `None` if this is the root item."""
        ...

    @abstractmethod
    def get_display_name(self) -> str:
        """Get the name displayed on the item."""
        ...

    @abstractmethod
    def get_icon(self) -> QIcon:
        """Get the icon displayed on the item."""
        ...

    @abstractmethod
    def supports_subitems(self) -> bool:
        """Whether the item supports subitems."""
        ...

    @abstractmethod
    def get_count(self) -> int:
        """Get the number of subitems."""
        ...

    def has_subitems(self) -> bool:
        """Whether this item contains subitems."""
        return not self.get_count() == 0

    @abstractmethod
    def index(self, item: SubItemType) -> int | None:
        """
        Try to find the index of **item** in this item's subitems. Returns `None` if **item** is not
        found.
        """
        ...

    @abstractmethod
    def get_subitem(self, index: int) -> SubItemType | None:
        """Get the subitem at **index**."""
        ...
        # try:
        #     return self.get_subitems()[index]
        # except Exception:
        #     return None

    def open_event(self):
        """
        Handle the item being "opened" (i.e. double clicked). By default this just expands the item
        (if it has subitems).
        """
        pass

    def expand_event(self):
        """Handle the item expanding."""
        pass

    def collapse_event(self):
        """Handle the item collapsing."""
        pass


class CategoryItem(TreeItem[TreeItem]):
    """
    An item representing a category. Categories do nothing by themselves; they just hold other
    items.
    """

    SUPPORTS_DRAGGING = False  # implementation
    COLLAPSED_ICON = images.make_icon("folder-horizontal.png")
    EXPANDED_ICON = images.make_icon("folder-horizontal-open.png")

    def __init__(self, parent: TreeItem | None, display_name: str, subitems: Sequence[TreeItem]):
        self.parent = parent
        self.display_name = display_name
        self.icon = self.COLLAPSED_ICON
        self.subitems = subitems

    @classmethod
    def create_root(cls, subitems: Sequence[TreeItem]) -> TreeItem:
        """Create the root item."""
        return cls(None, "", subitems)

    def get_parent(self) -> TreeItem | None:  # implementation
        return self.parent

    def get_display_name(self) -> str:  # implementation
        return self.display_name

    def get_icon(self) -> QIcon:  # implementation
        return self.icon

    def supports_subitems(self) -> bool:  # implementation
        return True

    def get_count(self) -> int:  # implementation
        return len(self.subitems)

    def index(self, item: TreeItem) -> int | None:  # implementation
        try:
            return self.subitems.index(item)
        except ValueError:
            return None

    def get_subitem(self, index: int) -> TreeItem | None:  # implementation
        try:
            return self.subitems[index]
        except IndexError:
            return None

    def expand_event(self):  # implementation
        self.icon = self.EXPANDED_ICON

    def collapse_event(self):  # implementation
        self.icon = self.COLLAPSED_ICON


class SequenceItem(TreeItem["SequenceItem"]):
    """An item that represents a sequence step."""

    SUPPORTS_DRAGGING = True  # implementation

    def __init__(self, parent: TreeItem, inner_item: Item):
        self.parent = parent
        self.item = inner_item
        self.enabled = True
        self.subitems: list[Self] = []

    @classmethod
    def from_dict(cls, parent: TreeItem, item_as_dict: dict[str, Any]) -> Self:
        """Create the item from a dictionary."""
        # deserialize the inner item
        inner_item: Item = serde.deserialize(item_as_dict[ITEM])
        item = cls(parent, inner_item)  # make the outer item
        # recursively deserialize all subitems
        subitems = [
            cls.from_dict(item, subitem_as_dict) for subitem_as_dict in item_as_dict[SUBITEMS]
        ]
        item.append_subitems(subitems)  # add them to the outer item
        return item

    def as_dict(self) -> dict[str, Any]:
        """Convert the item to a dictionary."""
        return {
            ITEM: self.item.as_dict(),
            SUBITEMS: [subitem.as_dict() for subitem in self.subitems],
        }

    def get_parent(self) -> TreeItem | None:  # implementation
        return self.parent

    def get_display_name(self) -> str:  # implementation
        return self.item.get_display_name()

    def get_icon(self) -> QIcon:  # implementation
        return self.item.get_icon()

    def supports_subitems(self) -> bool:
        return self.item.SUPPORTS_SUBITEMS

    def get_count(self) -> int:  # implementation
        return len(self.subitems)

    def index(self, item: Self) -> int | None:  # implementation
        # this cast is safe because SequenceItems only ever contain other SequenceItems
        try:
            return self.subitems.index(item)
        except ValueError:
            return None

    def get_subitem(self, index: int) -> Self | None:  # implementation
        try:
            return self.subitems[index]
        except IndexError:
            return None

    def open_event(self):  # implementation
        self.item.open_event()

    def set_enabled(self, enabled: bool):
        """Set whether the item is enabled."""
        self.enabled = enabled

    def is_enabled(self) -> bool:
        """Whether the item is enabled."""
        return self.enabled

    # def create_process(self) -> ...:  # TODO: type annotate
    #     """Create the process this item represents."""
    #     return self.item.create_process()

    def append_subitems(self, items: Sequence[Self]):
        """Append all **items** to this item's list of subitems."""
        self.subitems.extend(items)

    # implementation
    def insert_subitems(self, starting_row_index: int, items: Sequence[Self]) -> bool:
        """
        Insert all **items** starting at **starting_row_index**, with the newest subitems on
        top. Returns whether the operation succeeded.
        """
        try:
            for i, item in enumerate(items):
                self.subitems.insert(starting_row_index + i, item)
        except Exception:
            return False
        return True

    def remove_subitems(self, starting_row_index: int, count: int):
        """
        Remove **count** subitems starting at **starting_row_index**. Returns whether the operation
        succeeded.
        """
        try:
            for _ in range(count):
                self.subitems.pop(starting_row_index)
        except Exception:
            return False
        return True
