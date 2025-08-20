from fabrial import PluginCategory

# notice we import our item
from .random_item import RandomDataItem


def categories() -> list[PluginCategory]:
    # we use "Random" as the name of the category
    # when creating the `RandomDataItem`, we use 5 as the default value
    return [PluginCategory("Random", [RandomDataItem(5)])]
