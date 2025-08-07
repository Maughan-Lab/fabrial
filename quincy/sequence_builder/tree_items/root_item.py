from typing import Iterable, Self, Sequence

from ...utility.serde import Json
from . import tree_item
from .sequence_item import SequenceItem
from .tree_item import TreeItem

ITEMS = "items"

type SubItemType = TreeItem[SequenceItem]


class RootItem[SubItem: SubItemType](TreeItem[SubItem]):
    SUPPORTS_DRAGGING = False

    def __init__(self):
        self.subitems: list[SubItem] = []

    def serialize(self) -> Sequence[Json]:  # implementation
        return [subitem.serialize() for subitem in self.subitems]

    def get_parent(self) -> TreeItem[Self] | None:  # implementation
        return None

    def set_parent(self, parent: TreeItem[Self] | None):
        if parent is not None:
            raise NotImplementedError("The parent of a `RootItem` must always be `None`")

    def get_count(self) -> int:  # implementation
        return len(self.subitems)

    def index(self, item: SubItem) -> int | None:  # implementation
        return tree_item.index(self.subitems, item)

    def get_subitem(self, index) -> SubItem | None:  # implementation
        return tree_item.get_subitem(self.subitems, index)

    def append_subitems(self, items: Iterable[SubItem]):  # implementation
        tree_item.append_subitems(self, self.subitems, items)

    def insert_subitems(self, starting_row_index: int, items: Iterable[SubItem]):  # implementation
        tree_item.insert_subitems(self, self.subitems, starting_row_index, items)

    def remove_subitems(self, starting_row_index: int, count: int):  # implementation
        tree_item.remove_subitems(self.subitems, starting_row_index, count)
