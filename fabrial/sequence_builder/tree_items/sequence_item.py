from __future__ import annotations

import typing
from collections.abc import Iterable, Mapping
from typing import Self

from PyQt6.QtGui import QIcon

from ...classes import SequenceStep
from ...constants.sequence_builder import SUBITEMS
from ...utility import serde
from ...utility.serde import Json
from ..data_item import DataItem
from . import tree_item
from .tree_item import MutableTreeItem, TreeItem

ITEM = "item"


class SequenceItem(MutableTreeItem["SequenceItem"]):
    """An item that represents a sequence step."""

    def __init__(self, parent: TreeItem | None, data_item: DataItem):
        self.parent_item = parent
        self.item = data_item
        self.emphasized = False
        self.subitems: list[SequenceItem] = []

    @classmethod
    def from_dict(cls, parent: TreeItem, item_as_dict: Mapping[str, Json]) -> Self:
        """Create the item from a JSON dictionary."""
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

    def serialize(self) -> dict[str, Json]:  # implementation
        return {
            ITEM: self.item.serialize_tagged(),
            SUBITEMS: [subitem.serialize() for subitem in self.subitems],
        }

    def parent(self) -> TreeItem | None:  # implementation
        return self.parent_item

    def set_parent(self, parent: TreeItem | None):
        self.parent_item = parent

    def display_name(self) -> str:  # overridden
        return self.item.display_name()

    def icon(self) -> QIcon:  # overridden
        return self.item.icon()

    def supports_subitems(self) -> bool:  # overridden
        return self.item.supports_subitems()

    def supports_dragging(self) -> bool:  # overridden
        return True

    def subitem_count(self) -> int:  # implementation
        return len(self.subitems)

    def index(self, item: TreeItem) -> int | None:  # implementation
        return tree_item.index(self.subitems, item)

    def get_subitem(self, index: int) -> SequenceItem | None:  # implementation
        return tree_item.get_subitem(self.subitems, index)

    def append_subitems(self, items: Iterable[SequenceItem]):  # implementation
        tree_item.append_subitems(self, self.subitems, items)

    def insert_subitems(self, start: int, items: Iterable[SequenceItem]):  # implementation
        tree_item.insert_subitems(self, self.subitems, start, items)

    def remove_subitems(self, start: int, count: int):  # implementation
        tree_item.remove_subitems(self.subitems, start, count)

    def open_event(self, editable: bool) -> bool:  # overridden
        self.item.open_event(editable)
        return False

    def expand_event(self):
        self.item.expand_event()

    def collapse_event(self):
        self.item.collapse_event()

    def set_emphasized(self, emphasized: bool):
        """Set whether the item is emphasized."""
        self.emphasized = emphasized

    def is_emphasized(self) -> bool:
        """Whether the item is emphasized."""
        return self.emphasized

    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        """Create the `SequenceStep` this item represents."""
        return self.item.create_sequence_step(substeps)

    # debugging
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__} {{ "
            f"emphasized: {self.is_emphasized()!r}, "
            f"item: {self.item!r}, "
            f"subitems: {self.subitems!r} }}"
        )
