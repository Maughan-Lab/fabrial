from quincy.utility.sequence_builder import PluginCategory

from .items import HoldItem


def categories() -> list[PluginCategory]:
    """Get the categories for this plugin."""
    return [PluginCategory("Flow Control", [HoldItem(0, 0, 0)])]
