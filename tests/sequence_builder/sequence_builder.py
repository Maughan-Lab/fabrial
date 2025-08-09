import os
import typing
from pathlib import Path
from typing import Mapping, Self, Sequence

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from pytest import fixture

from quincy.classes import Process
from quincy.sequence_builder.data_item import DataItem
from quincy.sequence_builder.tree_items import CategoryItem, SequenceItem
from quincy.utility import sequence_builder
from quincy.utility.serde import Json


class MockDataItem(DataItem):
    """A `DataItem` implementation for testing."""

    def __init__(self, name: str, number: int):
        self.name = name
        self.number = number

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:  # implementation
        return cls(
            typing.cast(str, serialized_obj["name"]), typing.cast(int, serialized_obj["number"])
        )

    def serialize(self) -> dict[str, Json]:  # implementation
        return {"name": self.name, "number": self.number}

    def get_display_name(self) -> str:  # implementation
        return self.name

    def get_icon(self) -> QIcon:  # implementation
        return QIcon()

    def open_event(self, editable: bool):  # implementation
        return  # do nothing

    def create_process(self) -> Process:
        raise NotImplementedError("`create_process()` called on `MockDataItem`")

    # testing
    def __eq__(self, other: Self):  # type: ignore
        return self.name == other.name and self.number == other.number


@fixture
def expected_structure() -> Sequence[CategoryItem]:
    """Provides the expected structure for `test_items_from_directories()`."""
    return [
        CategoryItem(
            None,
            "category1",
            [
                SequenceItem(None, MockDataItem("dir1item1", 11)),
                SequenceItem(None, MockDataItem("dir1item2", 12)),
            ],
        ),
        CategoryItem(
            None,
            "category2",
            [
                SequenceItem(None, MockDataItem("dir2item1", 21)),
                SequenceItem(None, MockDataItem("dir2item2", 22)),
                # category2 should have extra items because of a duplicate category
                SequenceItem(None, MockDataItem("dir4item1", 41)),
                SequenceItem(None, MockDataItem("dir4item2", 42)),
            ],
        ),
        # category5 should be here because nested categories are flattened
        CategoryItem(
            None,
            "category5",
            [
                SequenceItem(None, MockDataItem("dir5item1", 51)),
                SequenceItem(None, MockDataItem("dir5item2", 52)),
            ],
        ),
    ]


# this uses the `qapp` fixture to automatically create a `QApplication` instance, which is needed
# for the `QIcon`s in `CategoryItem`s
def test_items_from_directories(qapp: QApplication, expected_structure: Sequence[CategoryItem]):
    """Tests `utility.sequence_builder.items_from_directories()`."""
    ITEMS_DIR = Path(__file__).parent.joinpath("test_items")
    DIRECTORIES = [ITEMS_DIR.joinpath(directory_name) for directory_name in os.listdir(ITEMS_DIR)]

    items = sequence_builder.items_from_directories(DIRECTORIES)

    assert len(items) == len(expected_structure)  # assertion
    for actual, expected in zip(items, expected_structure):
        assert actual.get_display_name() == expected.get_display_name()  # assertion
        assert actual.get_count() == expected.get_count()  # assertion
        assert actual.get_parent() is None  # assertion
        for i in range(expected.get_count()):
            actual_inner = actual.get_subitem(i)
            expected_inner = expected.get_subitem(i)
            assert actual_inner is not None and expected_inner is not None  # assertion
            assert actual_inner.get_count() == 0  # assertion
            assert actual_inner.get_parent() is actual  # assertion
            # I don't love checking a "private" attribute here
            # TODO: find a better solution
            assert actual_inner.item == expected_inner.item  # assertion
