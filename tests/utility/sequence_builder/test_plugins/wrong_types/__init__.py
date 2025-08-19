from fabrial.utility.sequence_builder import PluginCategory

from ...mock_item import MockDataItem


def categories():
    return [
        # simulates someone not using a type checker (please for the love of god use a type checker)
        PluginCategory(
            "Wrong Types", [{"wrong": "type"}, MockDataItem("WrongTypes1", 0)]  # type: ignore
        ),
        PluginCategory(
            "Right Types", [MockDataItem("RightTypes1", 1), MockDataItem("RightTypes2", 2)]
        ),
    ]
