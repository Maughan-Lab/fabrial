from fabrial.utility.sequence_builder import PluginCategory

from ...mock_item import MockDataItem


def categories() -> list[PluginCategory]:
    # intentionally out of order
    return [
        PluginCategory(
            "Outer Category",
            [MockDataItem("Category2Outer", 2)],
            subcategories=[
                PluginCategory(
                    "Nested Category",
                    [MockDataItem("Category2Item2", 22), MockDataItem("Category2Item1", 21)],
                )
            ],
        ),
    ]
