from enum import Enum, unique
from typing import Self

# temperature
from . import electrochemistry, flow_control, temperature
from .base_widget import AbstractWidget, CategoryWidget


@unique
class ItemType(Enum):
    """Class for bridging between file contents and actual TreeItems."""

    # root
    ROOT = CategoryWidget
    # EIS
    ELECTROCHEMISTRY_CATEGORY = electrochemistry.category_widget.ElectrochemistryCategoryWidget
    EIS = electrochemistry.EIS.widget.EISWidget
    # flow control
    FLOW_CONTROL_CATEGORY = flow_control.category_widget.FlowControlCategoryWidget
    LOOP = flow_control.loop.widget.LoopWidget
    HOLD = flow_control.hold.widget.HoldWidget
    # temperature
    TEMPERATURE_CATEGORY = temperature.category_widget.TemperatureCategoryWidget
    SET_TEMPERATURE = temperature.set_temperature.widget.SetTemperatureWidget
    INCREMENT_TEMPERATURE = temperature.increment_temperature.widget.IncrementTemperatureWidget
    BACKGROUND_TEMPERATURE = temperature.background_temperature.widget.BackgroundTemperatureWidget
    SET_NO_STABILIZE = temperature.set_no_stabilize.widget.SetNoStabilizeWidget

    @classmethod
    def from_name(cls: type[Self], name: str) -> Self:
        """Use this method to go from a file to an item."""
        return cls[name]

    @classmethod
    def from_widget(cls: type[Self], widget: AbstractWidget) -> Self:
        """Use this method to go from an item to a file."""
        return cls(type(widget))
