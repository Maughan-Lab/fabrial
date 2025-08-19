from fabrial.utility.sequence_builder import PluginCategory

from ...mock_item import MockDataItem


def categories() -> list[PluginCategory]:
    # intentionally out of order
    return [
        PluginCategory("Normal2", [MockDataItem("Normal22", 22), MockDataItem("Normal21", 21)]),
        PluginCategory("Normal1", [MockDataItem("Normal11", 11), MockDataItem("Normal12", 12)]),
    ]
