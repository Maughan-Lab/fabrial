from enum import Enum, unique
from typing import Self
from .base.item_info import BaseItemInfo
from .root.item_info import RootItemInfo
from .EIS.item_info import EISItemInfo
from .test.item_info import TestItemInfo
from .loop.item_info import LoopItemInfo


@unique
class TypeInfo(Enum):
    """Class for bridging between file contents and actual TreeItems."""

    ROOT = RootItemInfo
    EIS = EISItemInfo
    TEST = TestItemInfo
    LOOP = LoopItemInfo

    @classmethod
    def from_name(cls: type[Self], name: str) -> Self:
        # use this method to go from a file to an item
        return cls[name]

    @classmethod
    def from_item_info(cls: type[Self], item_info: type[BaseItemInfo]) -> Self:
        # use this method to go from an item to a file
        return cls(item_info)
