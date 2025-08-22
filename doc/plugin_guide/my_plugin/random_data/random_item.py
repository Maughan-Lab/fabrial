import typing
from collections.abc import Iterable, Mapping
from typing import Self

from fabrial import Json, SequenceStep, WidgetDataItem

from .random_step import RandomDataStep

# notice that we import our widget too
from .random_widget import RandomDataWidget

# this constant is used for serializing and deserializing later
DATA_INTERVAL_KEY = "data_interval"


# we inherit from `WidgetDataItem` so Fabrial can use the item
class RandomDataItem(WidgetDataItem):
    """Record random data on an interval; item."""

    def __init__(self, data_interval: float):
        # the only thing we need to do here is create the widget
        self.random_data_widget = RandomDataWidget(data_interval)

    def serialize(self) -> dict[str, Json]:
        # we store the data interval in a dictionary
        return {DATA_INTERVAL_KEY: self.random_data_widget.interval_spinbox.value()}

    @classmethod  # notice the `@classmethod` decorator. You must have this
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:
        # `cls` is the class, `RandomDataItem` in this case

        # we extract the data interval from the serialized object
        # notice how we use the same dictionary key as in `serialize()`
        data_interval = serialized_obj[DATA_INTERVAL_KEY]
        # `typing.cast()` is for type checkers; it is optional if you
        # aren't type checking
        return cls(typing.cast(float, data_interval))
        # the above line is equivalent to
        # `return RandomDataItem(data_interval)`

    def widget(self) -> RandomDataWidget:
        # this is just a getter for the widget
        return self.random_data_widget

    # the `substeps` parameter is always an empty list for items that don't
    # support subitems. If the item does supports subitems, those items will be
    # converted into sequence steps and passed to this function
    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        return RandomDataStep(self.random_data_widget.interval_spinbox.value())
