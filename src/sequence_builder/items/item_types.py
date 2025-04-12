from enum import Enum, unique
from typing import Self

from .base_widget import BaseWidget, CategoryWidget

# flow control
from .flow_control.category_widget import FlowControlCategoryWidget
from .flow_control.loop.widget import LoopWidget

# EIS
from .EIS.category_widget import EISCategoryWidget
from .EIS.EIS.widget import EISWidget

# oven control
from .oven_control.category_widget import OvenControlCategoryWidget
from .oven_control.set_temperature.widget import SetTemperatureWidget

# test
from .test.widget import TestWidget


@unique
class ItemType(Enum):
    """Class for bridging between file contents and actual TreeItems."""

    # root
    ROOT = CategoryWidget
    # EIS
    EIS_CATEGORY = EISCategoryWidget
    EIS = EISWidget
    # test
    TEST = TestWidget
    # flow control
    FLOW_CONTROL_CATEGORY = FlowControlCategoryWidget
    LOOP = LoopWidget
    # oven control
    OVEN_CONTROL_CATEGORY = OvenControlCategoryWidget
    SET_TEMPERATURE = SetTemperatureWidget

    @classmethod
    def from_name(cls: type[Self], name: str) -> Self:
        # use this method to go from a file to an item
        return cls[name]

    @classmethod
    def from_widget(cls: type[Self], widget: BaseWidget | CategoryWidget) -> Self:
        # use this method to go from an item to a file
        return cls(type(widget))
