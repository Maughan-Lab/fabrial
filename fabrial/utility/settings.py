import logging
from collections.abc import Callable, Mapping
from types import ModuleType

from ..custom_widgets.settings import PluginSettingsWidget


def load_settings_widgets(
    plugins: Mapping[str, ModuleType],
) -> tuple[dict[str, PluginSettingsWidget], list[str]]:
    """
    Load settings widgets from **plugins**. Logs errors.

    Returns
    -------
    A tuple of (a mapping of plugin names to the settings widget loaded from that plugin, the names
    of plugins with improper settings widget entry points).

    Notes
    -----
    Since the settings widget entry point is optional, plugins that do not provide a settings widget
    are not included in the list of improper plugins.
    """
    settings_widgets: dict[str, PluginSettingsWidget] = {}
    failed_plugins: list[str] = []

    for plugin_name, plugin_module in plugins.items():
        try:
            settings_entry_point: Callable[[], PluginSettingsWidget] = plugin_module.settings_widget
        except AttributeError:  # the plugin doesn't provide a settings widget, skip
            continue
        try:
            settings_widget = settings_entry_point()
            # make sure it's actually a `PluginSettingsWidget`
            assert isinstance(settings_widget, PluginSettingsWidget)
            settings_widgets[plugin_name] = settings_widget
        except Exception:
            logging.getLogger(__name__).exception(
                f"Failed to load settings widget from plugin {plugin_name}"
            )
            failed_plugins.append(plugin_name)

    return (settings_widgets, failed_plugins)
