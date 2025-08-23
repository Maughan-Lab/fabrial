from __future__ import annotations

import importlib
import json
import logging
import pkgutil
import sys
import typing
from collections.abc import Callable, Iterable, MutableMapping
from dataclasses import dataclass
from importlib import metadata
from importlib.metadata import EntryPoint
from os import PathLike
from types import ModuleType

from ..constants import PLUGIN_ENTRY_POINT, SAVED_DATA_FOLDER
from ..constants.paths.settings.plugins import GLOBAL_PLUGINS_FILE, LOCAL_PLUGINS_FILE
from ..custom_widgets.settings import PluginSettingsWidget
from . import errors, sequence_builder, settings
from .sequence_builder import CategoryItem


@dataclass
class PluginSettings:
    """Local and global plugin settings."""

    global_settings: dict[str, bool]
    local_settings: dict[str, bool]


def discover_plugins_from_module(module: ModuleType) -> dict[str, Callable[[], ModuleType]]:
    """
    Discover plugins in a module.

    Parameters
    ----------
    module
        The module to search in.

    Returns
    -------
    A mapping of plugin names to a function that will import the plugin.
    """

    def load_function_factory(module_name: str) -> Callable[[], ModuleType]:
        return lambda: importlib.import_module(module_name)

    return {
        name: load_function_factory(f"{module.__name__}.{name}")
        for _, name, is_package in pkgutil.iter_modules(module.__path__)
        if is_package
    }


def discover_global_plugins() -> dict[str, Callable[[], ModuleType]]:
    """
    Discover global plugins from the **`plugins`** folder.

    Returns
    -------
    A mapping of plugin names to a function that will import the plugin.
    """
    try:
        # add the application's storage directory to sys.path
        sys.path.append(str(SAVED_DATA_FOLDER))
        # since the storage directory is in sys.path, we can import `plugins` from it
        local_plugins_module = importlib.import_module("plugins")
        return discover_plugins_from_module(local_plugins_module)
    except Exception:  # if the `plugins` folder doesn't exist, just ignore it
        return {}


def discover_local_plugins() -> dict[str, Callable[[], ModuleType]]:
    """
    Discover local plugins (i.e. plugins installed via `pip`).

    Returns
    -------
    A mapping of plugin names to a function that will import the plugin.
    """

    def load_function_factory(entry_point: EntryPoint) -> Callable[[], ModuleType]:
        return lambda: entry_point.load()

    return {
        entry_point.module: load_function_factory(entry_point)
        for entry_point in metadata.entry_points(group=PLUGIN_ENTRY_POINT)
    }


def discover_plugins() -> (
    tuple[dict[str, Callable[[], ModuleType]], dict[str, Callable[[], ModuleType]]]
):
    """
    Discover all plugins for the application, with local plugins shadowing global plugins.

    Returns
    -------
    A tuple of (global plugins, local plugins). Each entry in the tuple is a mapping of plugin
    names to a function that will import the plugin.
    """
    local_plugins = discover_local_plugins()
    global_plugins = discover_global_plugins()

    # remove duplicate names from the global plugins
    for plugin_name in set(local_plugins).intersection(global_plugins):
        # not using a default because the keys must be in the dictionary
        global_plugins.pop(plugin_name)

    return (global_plugins, local_plugins)


def load_plugin_settings(file: PathLike[str] | str, plugin_names: Iterable[str]) -> dict[str, bool]:
    """
    Load plugin settings, removing entries for non-installed plugins and adding entries for newly
    installed plugins.

    Parameters
    ----------
    file
        The JSON file containing the plugin settings.
    plugin_names
        The discovered plugin names.

    Returns
    The plugin settings.
    """
    try:
        with open(file, "r") as f:
            plugin_settings = typing.cast(dict[str, bool], json.load(f))
        # only include plugins from **plugins**. If the file did not contain an entry for a plugin,
        # assume the plugin is enabled
        return {name: plugin_settings.pop(name, True) for name in plugin_names}
    except Exception:  # if the file couldn't be loaded, all plugins are enabled
        logging.getLogger(__name__).info(
            f"Failed to read plugin settings file: {file}", exc_info=True
        )
        return {name: True for name in plugin_names}


def load_plugins(
    plugins: MutableMapping[str, Callable[[], ModuleType]], plugin_settings: dict[str, bool]
) -> tuple[dict[str, ModuleType], list[str]]:
    """
    Load **plugins** by calling each loading function.

    Parameters
    ----------
    plugins
        A mapping of plugin names to a function that will load the plugin. This function removes all
        items from this mapping.
    plugin_settings
        A mapping of plugin names to whether the plugin is enabled.

    Returns
    -------
    A tuple of (the loaded plugins, the names of plugins that could not be loaded).

    Raises
    ------
    IndexError
        **plugin_settings** does not contain all of the keys in **plugins**.
    """
    loaded_plugins: dict[str, ModuleType] = {}
    failed_plugins: list[str] = []

    while len(plugins) > 0:
        # remove an item from **plugins**
        plugin_name, loader_command = plugins.popitem()
        # if the entry isn't present the application should crash
        should_load = plugin_settings[plugin_name]
        if not should_load:
            continue  # don't load the plugin
        try:
            loaded_plugins[plugin_name] = loader_command()
        except Exception:
            logging.getLogger(__name__).exception(f"Error while loading plugin {plugin_name}")
            failed_plugins.append(plugin_name)

    return (loaded_plugins, failed_plugins)


def load_all_plugins() -> (
    tuple[list[CategoryItem], dict[str, PluginSettingsWidget], PluginSettings]
):
    """
    Load all plugins.

    Returns
    -------
    A tuple of (the loaded `CategoryItem`s, a mapping of plugin names to the loaded settings menu
    for that plugin, the plugin settings).
    """
    # discover plugins
    global_names, local_names = discover_plugins()
    # load plugin settings (i.e. if plugins are enabled or disabled)
    global_settings = load_plugin_settings(GLOBAL_PLUGINS_FILE, global_names.keys())
    local_settings = load_plugin_settings(LOCAL_PLUGINS_FILE, local_names.keys())
    # load the plugins
    global_plugins, failed_globals = load_plugins(global_names, global_settings)
    local_plugins, failed_locals = load_plugins(local_names, local_settings)
    # combine plugins (no more separation between global and local)
    plugins = global_plugins | local_plugins
    failed_plugins = failed_locals + failed_globals
    # possibly report an error to the user
    if len(failed_plugins) > 0:
        errors.show_error_delayed(
            "Plugin Error",
            f"Failed to load plugins:\n\n{", ".join(failed_plugins)}\n\n"
            "See the error log for details.",
        )

    # load items from plugins
    items, failed_plugins = sequence_builder.items_from_plugins(plugins)
    # possibly report an error to the user
    if len(failed_plugins) > 0:
        errors.show_error_delayed(
            "Plugin Items Error",
            f"Failed to load items from plugins:\n\n{", ".join(failed_plugins)}\n\n"
            "See the error log for details.",
        )

    # load settings widgets from plugins
    settings_widgets, failed_plugins = settings.load_settings_widgets(plugins)
    # possibly report an error to the user
    if len(failed_plugins) > 0:
        errors.show_error_delayed(
            "Plugin Settings Error",
            f"Invalid settings widget from plugins:\n\n{", ".join(failed_plugins)}\n\n"
            "See the error log for details.",
        )

    return (items, settings_widgets, PluginSettings(global_settings, local_settings))
