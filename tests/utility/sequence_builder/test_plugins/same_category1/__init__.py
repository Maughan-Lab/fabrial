from fabrial.utility.sequence_builder import PluginCategory

from ...mock_item import MockDataItem


def categories() -> list[PluginCategory]:
    # intentionally out of order
    return [
        PluginCategory(
            "Outer Category",
            [MockDataItem("Category1Outer", 1)],
            subcategories=[
                PluginCategory(
                    "Nested Category",
                    [MockDataItem("Category1Item2", 12), MockDataItem("Category1Item1", 11)],
                )
            ],
        ),
    ]
