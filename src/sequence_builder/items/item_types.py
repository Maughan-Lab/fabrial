from enum import Enum, unique
from typing import Self

from .base_widget import AbstractWidget, CategoryWidget

# flow control
from .flow_control.category_widget import FlowControlCategoryWidget
from .flow_control.loop.widget import LoopWidget

# EIS
from .electrochemistry.category_widget import ElectrochemistryCategoryWidget
from .electrochemistry.EIS.widget import EISWidget

# oven control
from .temperature.category_widget import TemperatureCategoryWidget
from .temperature.set_temperature.widget import SetTemperatureWidget
from .temperature.increment_temperature.widget import IncrementTemperatureWidget

# test
from .test.widget import TestWidget


@unique
class ItemType(Enum):
    """Class for bridging between file contents and actual TreeItems."""

    # root
    ROOT = CategoryWidget
    # EIS
    ELECTROCHEMISTRY_CATEGORY = ElectrochemistryCategoryWidget
    EIS = EISWidget
    # test
    TEST = TestWidget
    # flow control
    FLOW_CONTROL_CATEGORY = FlowControlCategoryWidget
    LOOP = LoopWidget
    # oven control
    TEMPERATURE_CATEGORY = TemperatureCategoryWidget
    SET_TEMPERATURE = SetTemperatureWidget
    INCREMENT_TEMPERATURE = IncrementTemperatureWidget

    @classmethod
    def from_name(cls: type[Self], name: str) -> Self:
        """Use this method to go from a file to an item."""
        return cls[name]

    @classmethod
    def from_widget(cls: type[Self], widget: AbstractWidget) -> Self:
        """Use this method to go from an item to a file."""
        return cls(type(widget))
