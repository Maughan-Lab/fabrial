from typing import Iterable

from PyQt6.QtWidgets import QApplication
from pytest import FixtureRequest, fixture, mark

from fabrial.sequence_builder.tree_items import CategoryItem, SequenceItem, TreeItem
from fabrial.utility import sequence_builder

from .mock_item import MockDataItem
from .test_plugins import (
    empty_categories,
    no_entry_point,
    normal,
    same_category1,
    same_category2,
    wrong_entry_point_type,
    wrong_types,
)


def compare_items(actual: Iterable[CategoryItem], expected: Iterable[CategoryItem]):
    # helper to compare just the items and their parents, not the subitems
    def compare(actual: TreeItem, expected: TreeItem):
        # check the parents
        actual_parent = actual.parent()
        expected_parent = expected.parent()
        if actual_parent is None or expected_parent is None:
            assert actual_parent is None and expected_parent is None
        else:
            compare(actual_parent, expected_parent)

        # if one is a `CategoryItem` they should both be `CategoryItem`s
        if isinstance(actual, CategoryItem) or isinstance(expected, CategoryItem):
            assert type(actual) is type(expected)
            assert actual.display_name() == expected.display_name()
        else:  # otherwise they most both be `SequenceItem`s
            assert isinstance(actual, SequenceItem) and isinstance(expected, SequenceItem)
            # I don't love checking a "private" attribute here
            # TODO: find a better solution
            assert actual.item == expected.item

    # helper to compare the items, their parents, and their subitems
    def recursive_compare(actual: TreeItem, expected: TreeItem):
        compare(actual, expected)
        # check the counts
        actual_count = actual.subitem_count()
        assert actual_count == expected.subitem_count()
        for i in range(actual_count):
            sub_actual = actual.get_subitem(i)
            sub_expected = expected.get_subitem(i)
            # this line assumes that all subitems within the range should be valid
            assert sub_actual is not None and sub_expected is not None
            compare(sub_actual, sub_expected)
            recursive_compare(sub_actual, sub_expected)

    for actual_item, expected_item in zip(actual, expected, strict=True):
        recursive_compare(actual_item, expected_item)


@fixture
def expected(request: FixtureRequest):
    """Provides the expected result on a per-test basis."""
    normal = [
        CategoryItem(
            None,
            "Normal1",
            [
                SequenceItem(None, MockDataItem("Normal11", 11)),
                SequenceItem(None, MockDataItem("Normal12", 12)),
            ],
        ),
        CategoryItem(
            None,
            "Normal2",
            [
                SequenceItem(None, MockDataItem("Normal21", 21)),
                SequenceItem(None, MockDataItem("Normal22", 22)),
            ],
        ),
    ]

    same_category = [
        CategoryItem(
            None,
            "Outer Category",
            [
                CategoryItem(
                    None,
                    "Nested Category",
                    [
                        SequenceItem(None, MockDataItem("Category1Item1", 11)),
                        SequenceItem(None, MockDataItem("Category1Item2", 12)),
                        SequenceItem(None, MockDataItem("Category2Item1", 21)),
                        SequenceItem(None, MockDataItem("Category2Item2", 22)),
                    ],
                ),
                SequenceItem(None, MockDataItem("Category1Outer", 1)),
                SequenceItem(None, MockDataItem("Category2Outer", 2)),
            ],
        )
    ]

    everything = normal + same_category

    function = request.function
    if function is test_normal:
        return normal
    elif function is test_same_category:
        return same_category
    elif function is test_everything:
        return everything
    raise ValueError("A test used the `expected()` fixture but is not registered for that fixture")


# --------------------------------------------------------------------------------------------------
# tests start here
def test_normal(qapp: QApplication, expected: Iterable[CategoryItem]):
    """Tests a normal, functioning plugin."""
    items, failure_plugins = sequence_builder.items_from_plugins({normal.__name__: normal})
    assert len(failure_plugins) == 0  # no failures expected
    compare_items(items, expected)


def test_empty():
    """Tests a plugin that returns an empty list of categories."""
    items, failure_plugins = sequence_builder.items_from_plugins(
        {empty_categories.__name__: empty_categories}
    )
    assert len(failure_plugins) == 0  # no failures expected
    assert len(items) == 0  # should just be an empty list


def test_no_entry_point():
    """Tests a plugin that is missing the `categories()` entry point."""
    items, failure_plugins = sequence_builder.items_from_plugins(
        {no_entry_point.__name__: no_entry_point}
    )
    assert len(items) == 0 and len(failure_plugins) == 1
    assert no_entry_point.__name__ in failure_plugins


def test_wrong_entry_point_type():
    """Tests a plugin that returns the wrong type from its entry point."""
    items, failure_plugins = sequence_builder.items_from_plugins(
        {wrong_entry_point_type.__name__: wrong_entry_point_type}
    )
    assert len(items) == 0 and len(failure_plugins) == 1
    assert wrong_entry_point_type.__name__ in failure_plugins


def test_same_category(qapp: QApplication, expected: Iterable[CategoryItem]):
    """
    Tests a plugin with nested categories that share names (so they should all be grouped together).
    """
    items, failure_plugins = sequence_builder.items_from_plugins(
        {same_category1.__name__: same_category1, same_category2.__name__: same_category2}
    )
    assert len(failure_plugins) == 0
    compare_items(items, expected)


def test_everything(qapp: QApplication, expected: Iterable[CategoryItem]):
    """Tests EVERYTHING! (aka tests the combination of all prior modules)."""
    items, failure_plugins = sequence_builder.items_from_plugins(
        {
            module.__name__: module
            for module in [
                # arbitrary order
                empty_categories,
                no_entry_point,
                normal,
                same_category1,
                same_category2,
                wrong_entry_point_type,
            ]
        }
    )

    assert len(failure_plugins) == 2
    assert (
        no_entry_point.__name__ in failure_plugins
        and wrong_entry_point_type.__name__ in failure_plugins
    )
    compare_items(items, expected)


@mark.xfail(raises=AttributeError)  # expected to fail
def test_wrong_types(qapp: QApplication):
    """Tests a plugin that returns the correct entry point type, but an item has the wrong type."""
    sequence_builder.items_from_plugins({wrong_types.__name__: wrong_types})
    # we don't check anything because this test should fail
