from collections.abc import Callable, Mapping
from types import ModuleType

from PyQt6.QtWidgets import QWidget


def load_settings_widgets(plugins: Mapping[str, ModuleType]) -> tuple[list[QWidget], list[str]]:
    """
    Load settings widgets from **plugins**.

    Returns
    -------
    A tuple of (the loaded settings widgets, the names of plugins with improper settings widget
    entry points).

    Notes
    -----
    Since the settings widget entry point is optional, plugins that do not provide a settings widget
    are not included in the list of improper plugins.
    """
    settings_widgets: list[QWidget] = []
    failed_plugins: list[str] = []

    for plugin_name, plugin_module in plugins.items():
        try:
            settings_entry_point: Callable[[], QWidget] = plugin_module.settings_widget()
        except AttributeError:  # the plugin doesn't provide a settings widget, skip
            continue
        try:
            settings_widget = settings_entry_point()
            # make sure it's actually a `QWidget`
            assert isinstance(settings_widget, QWidget)
            settings_widgets.append(settings_widget)
        except Exception:
            failed_plugins.append(plugin_name)

    return (settings_widgets, failed_plugins)
