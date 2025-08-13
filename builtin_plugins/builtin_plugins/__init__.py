from QuincE import PluginCategory

from . import flow_control


def categories() -> list[PluginCategory]:
    """Get the categories for this plugin."""
    return flow_control.categories()
