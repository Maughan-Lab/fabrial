from collections.abc import Sequence

from PyQt6.QtGui import QIcon

from ...utility import images
from . import tree_item
from .tree_item import TreeItem


class CategoryItem(TreeItem):
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

    def __init__(self, parent: TreeItem | None, category_name: str, subitems: Sequence[TreeItem]):
        self.parent_item = parent
        self.name = category_name
        # these two need to be instance attributes instead of class attributes because you have to
        # construct a `QApplication` before a `QIcon`
        self.collapsed_icon = images.make_icon("folder-horizontal.png")
        self.expanded_icon = images.make_icon("folder-horizontal-open.png")

        self.item_icon = self.collapsed_icon
        for item in subitems:
            item.set_parent(self)
        self.subitems = subitems

    def serialize(self):  # implementation
        raise NotImplementedError("`CategoryItem`s do not support serialization")

    def parent(self) -> TreeItem | None:  # implementation
        return self.parent_item

    def set_parent(self, parent: TreeItem | None):  # implementation
        self.parent_item = parent

    def display_name(self) -> str:  # overridden
        return self.name

    def icon(self) -> QIcon:  # overridden
        return self.item_icon

    def subitem_count(self) -> int:  # implementation
        return len(self.subitems)

    def index(self, item: TreeItem) -> int | None:  # implementation
        return tree_item.index(self.subitems, item)

    def get_subitem(self, index: int) -> TreeItem | None:  # implementation
        return tree_item.get_subitem(self.subitems, index)

    def expand_event(self):  # overridden
        self.item_icon = self.expanded_icon

    def collapse_event(self):  # overridden
        self.item_icon = self.collapsed_icon

    # debugging
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} {{ "
            f"display_name: {self.display_name()!r}, "
            f"subitems: {self.subitems!r} }}"
        )
