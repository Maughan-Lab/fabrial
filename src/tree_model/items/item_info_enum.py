from enum import Enum, unique
from typing import Self


from .base.item_info import BaseItemInfo, CategoryInfo
from .test.item_info import TestItemInfo

# flow control
from .flow_control.category_info import FlowControlCategoryInfo
from .flow_control.loop.item_info import LoopItemInfo

# EIS
from .EIS.EIS.item_info import EISItemInfo
from .EIS.category_info import EISCategoryInfo


@unique
class ItemInfoType(Enum):
    """Class for bridging between file contents and actual TreeItems."""

    # root
    ROOT = CategoryInfo
    # EIS
    EIS_CATEGORY = EISCategoryInfo
    EIS = EISItemInfo
    # test
    TEST = TestItemInfo
    # flow control
    FLOW_CONTROL_CATEGORY = FlowControlCategoryInfo
    LOOP = LoopItemInfo

    @classmethod
    def from_name(cls: type[Self], name: str) -> Self:
        # use this method to go from a file to an item
        return cls[name]

    @classmethod
    def from_item_info(cls: type[Self], item_info: type[BaseItemInfo]) -> Self:
        # use this method to go from an item to a file
        return cls(item_info)
