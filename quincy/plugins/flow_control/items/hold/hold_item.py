import typing
from typing import Mapping, Self

from quincy.classes import Process
from quincy.sequence_builder import WidgetDataItem
from quincy.utility.serde import Json

from .hold_widget import HoldWidget

HOURS = "hours"
MINUTES = "minutes"
SECONDS = "seconds"


class HoldItem(WidgetDataItem):
    """Hold for a duration; item."""

    def __init__(self, hours: int, minutes: int, seconds: int):
        self.widget = HoldWidget(hours, minutes, seconds)

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        return cls(
            typing.cast(int, serialized_obj[HOURS]),
            typing.cast(int, serialized_obj[MINUTES]),
            typing.cast(int, serialized_obj[SECONDS]),
        )

    def serialize(self) -> dict[str, Json]:  # implementation
        return {
            HOURS: self.widget.hours_spinbox.value(),
            MINUTES: self.widget.minutes_spinbox.value(),
            SECONDS: self.widget.seconds_spinbox.value(),
        }

    def get_widget(self) -> HoldWidget:  # implementation
        return self.widget

    def create_process(self) -> Process:  # implementation
        raise NotImplementedError("AHHHH")
