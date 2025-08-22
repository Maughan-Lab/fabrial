from collections.abc import Iterable, Mapping
from typing import Self

from PyQt6.QtGui import QIcon

from fabrial import DataItem, Json, SequenceStep


class MockDataItem(DataItem):
    """A `DataItem` implementation for testing."""

    def __init__(self, name: str, number: int):
        self.name = name
        self.number = number

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        raise NotImplementedError("This shouldn't have been tested")

    def serialize(self) -> dict[str, Json]:  # implementation
        raise NotImplementedError("This shouldn't have been tested")

    def display_name(self) -> str:  # implementation
        return self.name

    def icon(self) -> QIcon:  # implementation
        raise NotImplementedError("This shouldn't have been tested")

    def open_event(self, editable: bool):  # implementation
        raise NotImplementedError("This shouldn't have been tested")

    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        raise NotImplementedError("`create_sequence_step()` called on `MockDataItem`")

    # testing
    def __eq__(self, other: Self):  # type: ignore
        return self.name == other.name and self.number == other.number

    # debugging
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {{ name: {self.name!r}, number: {self.number!r} }}"
