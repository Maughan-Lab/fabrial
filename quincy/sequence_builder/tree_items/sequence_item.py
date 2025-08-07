from __future__ import annotations

import typing
from typing import Iterable, Mapping, Self

from PyQt6.QtGui import QIcon

from ...classes import Process
from ...utility import serde
from ...utility.serde import Json
from ..data_item import DataItem
from . import tree_item
from .tree_item import MutableTreeItem, TreeItem

SUBITEMS = "subitems"
ITEM = "item"


class SequenceItem(MutableTreeItem["SequenceItem"]):
    """An item that represents a sequence step."""

    def __init__(self, parent: TreeItem[Self] | None, data_item: DataItem):
        self.parent: TreeItem | None = parent
        self.item = data_item
        self.active = False
        self.subitems: list[Self] = []

    @classmethod
    def from_dict(cls, parent: TreeItem[SequenceItem], item_as_dict: Mapping[str, Json]) -> Self:
        """Create the item from a dictionary."""
        # deserialize the inner item
        inner_item: DataItem = serde.deserialize(
            typing.cast(Mapping[str, Json], item_as_dict[ITEM])
        )
        item = cls(parent, inner_item)  # make the outer item
        # recursively deserialize all subitems
        subitems = [
            cls.from_dict(item, subitem_as_dict)
            for subitem_as_dict in typing.cast(Iterable[Mapping[str, Json]], item_as_dict[SUBITEMS])
        ]
        item.append_subitems(subitems)  # add them to the outer item
        return item

    def serialize(self) -> Mapping[str, Json]:  # implementation
        return {
            ITEM: self.item.serialize(),
            SUBITEMS: [subitem.serialize() for subitem in self.subitems],
        }

    def get_parent(self) -> TreeItem[Self] | None:  # implementation
        return self.parent

    def set_parent(self, parent: TreeItem[Self] | None):
        self.parent = parent

    def get_display_name(self) -> str:  # overridden
        return self.item.get_display_name()

    def get_icon(self) -> QIcon:  # overridden
        return self.item.get_icon()

    def supports_subitems(self) -> bool:  # overridden
        return self.item.supports_subitems()

    def supports_dragging(self) -> bool:  # overridden
        return True

    def get_count(self) -> int:  # implementation
        return len(self.subitems)

    def index(self, item: Self) -> int | None:  # implementation
        return tree_item.index(self.subitems, item)

    def get_subitem(self, index: int) -> Self | None:  # implementation
        return tree_item.get_subitem(self.subitems, index)

    def append_subitems(self, items: Iterable[Self]):  # implementation
        tree_item.append_subitems(self, self.subitems, items)

    def insert_subitems(self, starting_row_index: int, items: Iterable[Self]):  # implementation
        tree_item.insert_subitems(self, self.subitems, starting_row_index, items)

    def remove_subitems(self, starting_row_index: int, count: int):  # implementation
        tree_item.remove_subitems(self.subitems, starting_row_index, count)

    def open_event(self) -> bool:  # overridden
        self.item.open_event()
        return False

    def set_active(self, active: bool):
        """Set whether the item is active."""
        self.active = active

    def is_active(self) -> bool:
        """Whether the item is currently being run."""
        return self.active

    def create_process(self) -> Process:
        """Create the process this item represents."""
        return self.item.create_process()
