from typing import Self, Sequence

from PyQt6.QtGui import QIcon

from ...utility import images
from . import tree_item
from .sequence_item import SequenceItem
from .tree_item import TreeItem


class CategoryItem(TreeItem[SequenceItem]):
    """
    An item representing a category. Categories do nothing by themselves; they just hold other
    items.

    Parameters
    ----------
    parent
        The item's parent.
    category_name
        The name displayed on the item.
    subitems
        The item's subitems. The items' parent is automatically set to this item.
    """

    def __init__(
        self, parent: TreeItem[Self] | None, category_name: str, subitems: Sequence[SequenceItem]
    ):
        self.parent = parent
        self.display_name = category_name
        # these two need to be instance attributes instead of class attributes because you have to
        # construct a `QApplication` before a `QIcon`
        self.collapsed_icon = images.make_icon("folder-horizontal.png")
        self.expanded_icon = images.make_icon("folder-horizontal-open.png")

        self.icon = self.collapsed_icon
        for item in subitems:
            item.set_parent(self)
        self.subitems = subitems

    def serialize(self):  # implementation
        raise NotImplementedError("`CategoryItem`s do not support serialization")

    def get_parent(self) -> TreeItem[Self] | None:  # implementation
        return self.parent

    def set_parent(self, parent: TreeItem | None):  # implementation
        self.parent = parent

    def get_display_name(self) -> str:  # overridden
        return self.display_name

    def get_icon(self) -> QIcon:  # overridden
        return self.icon

    def get_count(self) -> int:  # implementation
        return len(self.subitems)

    def index(self, item: SequenceItem) -> int | None:  # implementation
        return tree_item.index(self.subitems, item)

    def get_subitem(self, index: int) -> SequenceItem | None:  # implementation
        return tree_item.get_subitem(self.subitems, index)

    def expand_event(self):  # overridden
        self.icon = self.expanded_icon

    def collapse_event(self):  # overridden
        self.icon = self.collapsed_icon
