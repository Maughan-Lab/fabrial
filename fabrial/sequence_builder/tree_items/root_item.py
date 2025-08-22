from collections.abc import Iterable

from ...utility.serde import Json
from . import tree_item
from .sequence_item import SequenceItem
from .tree_item import MutableTreeItem, TreeItem

ITEMS = "items"

type SubItemType = TreeItem[SequenceItem]


class RootItem[SubItem: TreeItem](MutableTreeItem[SubItem]):

    def __init__(self):
        self.subitems: list[SubItem] = []

    def serialize(self) -> list[Json]:  # implementation
        return [subitem.serialize() for subitem in self.subitems]

    def parent(self) -> TreeItem | None:  # implementation
        return None

    def set_parent(self, parent: TreeItem | None):
        if parent is not None:
            raise ValueError("The parent of a `RootItem` must always be `None`")

    def subitem_count(self) -> int:  # implementation
        return len(self.subitems)

    def index(self, item: TreeItem) -> int | None:  # implementation
        return tree_item.index(self.subitems, item)

    def get_subitem(self, index: int) -> SubItem | None:  # implementation
        return tree_item.get_subitem(self.subitems, index)

    def append_subitems(self, items: Iterable[SubItem]):  # implementation
        tree_item.append_subitems(self, self.subitems, items)

    def insert_subitems(self, start: int, items: Iterable[SubItem]):  # implementation
        tree_item.insert_subitems(self, self.subitems, start, items)

    def remove_subitems(self, start: int, count: int):  # implementation
        tree_item.remove_subitems(self.subitems, start, count)

    # debugging
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {{ subitems: {self.subitems!r} }}"
