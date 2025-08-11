import os
import typing
from pathlib import Path
from typing import Mapping, Self, Sequence

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication
from pytest import fixture

from quincy.classes import Process
from quincy.sequence_builder.data_item import DataItem
from quincy.sequence_builder.tree_items import CategoryItem, SequenceItem, TreeItem
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

    # debugging
    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {{ name: {self.name!r}, number: {self.number!r} }}"


@fixture
def items_directory() -> Path:
    """Provides the directory containing the test item directories."""
    return Path(__file__).parent.joinpath("test_items")


@fixture
def expected_structure() -> list[CategoryItem]:
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
                # category2 should have extra items because of a duplicate category in `dir4`
                SequenceItem(None, MockDataItem("dir4item1", 41)),
                SequenceItem(None, MockDataItem("dir4item2", 42)),
            ],
        ),
        CategoryItem(
            None,
            "category5",
            [
                # this category should be nested because of the file structure. It also appears
                # first because of sorting
                CategoryItem(
                    None,
                    "category6",
                    [
                        SequenceItem(None, MockDataItem("dir6item1", 61)),
                        SequenceItem(None, MockDataItem("dir6item2", 62)),
                    ],
                ),
                # these items appear after the category because of sorting
                SequenceItem(None, MockDataItem("dir5item1", 51)),
                SequenceItem(None, MockDataItem("dir5item2", 52)),
            ],
        ),
        # even though this category is nested, it should appear here because the parent folder
        # has no category file
        CategoryItem(
            None,
            "category7",
            [
                SequenceItem(None, MockDataItem("dir7item1", 71)),
                SequenceItem(None, MockDataItem("dir7item2", 72)),
            ],
        ),
        # this category should only have one item because one of the files is invalid
        CategoryItem(None, "failure_item", [SequenceItem(None, MockDataItem("failure_item2", 2))]),
    ]


@fixture
def expected_failures(items_directory: Path) -> list[Path]:
    """Provides a list of the expected failure paths."""
    return [
        Path(items_directory.joinpath("failure_dir")),
        Path(items_directory.joinpath("failure_item/item1.toml")),
    ]


# this uses the `qapp` fixture to automatically create a `QApplication` instance, which is needed
# for the `QIcon`s in `CategoryItem`s
def test_items_from_directories(
    qapp: QApplication,
    items_directory: Path,
    expected_structure: Sequence[CategoryItem],
    expected_failures: Sequence[Path],
):
    """Tests `utility.sequence_builder.items_from_directories()`."""

    def compare(actual: TreeItem, expected: TreeItem):
        # check the parents
        actual_parent = actual.get_parent()
        expected_parent = expected.get_parent()
        if actual_parent is None or expected_parent is None:
            assert actual_parent is None and expected_parent is None
        else:
            compare(actual_parent, expected_parent)

        # if one is a `CategoryItem` they should both be `CategoryItem`s
        if isinstance(actual, CategoryItem) or isinstance(expected, CategoryItem):
            assert type(actual) is type(expected)
            assert actual.get_display_name() == expected.get_display_name()
        else:  # otherwise they most both be `SequenceItem`s
            assert isinstance(actual, SequenceItem) and isinstance(expected, SequenceItem)
            # I don't love checking a "private" attribute here
            # TODO: find a better solution
            assert actual.item == expected.item

    def recursive_compare(actual: TreeItem, expected: TreeItem):
        compare(actual, expected)
        # check the counts
        actual_count = actual.get_count()
        assert actual_count == expected.get_count()
        for i in range(actual_count):
            sub_actual = actual.get_subitem(i)
            sub_expected = expected.get_subitem(i)
            # this line assumes that all subitems within the range should be valid
            assert sub_actual is not None and sub_expected is not None
            compare(sub_actual, sub_expected)
            recursive_compare(sub_actual, sub_expected)

    # get the list of directories to load
    DIRECTORIES = [
        items_directory.joinpath(directory_name)
        for directory_name in next(os.walk(items_directory))[1]
    ]
    # run the function
    items, failure_paths = sequence_builder.items_from_directories(DIRECTORIES)
    # make sure the failure paths are correct
    for expected_failure in expected_failures:
        # make sure the expected failure is in the list and there is only one instance
        assert failure_paths.count(expected_failure) == 1
    # make sure the items we got are what we were expecting
    for actual, expected in zip(items, expected_structure, strict=True):
        recursive_compare(actual, expected)
