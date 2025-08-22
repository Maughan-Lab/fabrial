from __future__ import annotations

import importlib
import json
import logging
import pkgutil
import sys
import typing
from collections.abc import Callable, Iterable, MutableMapping
from importlib import metadata
from os import PathLike
from types import ModuleType

from PyQt6.QtWidgets import QWidget

from ..constants import PLUGIN_ENTRY_POINT, SAVED_DATA_FOLDER
from ..constants.paths.settings.plugins import GLOBAL_PLUGINS_FILE, LOCAL_PLUGINS_FILE
from . import errors, sequence_builder
from .sequence_builder import CategoryItem


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
    return {
        name: lambda: importlib.import_module(f"{module.__name__}.{name}")
        for _, name, is_package in pkgutil.iter_modules(module.__path__)
        if is_package
    }


def discover_local_plugins() -> dict[str, Callable[[], ModuleType]]:
    """
    Discover local plugins from the `plugins` folder.

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


def discover_global_plugins() -> dict[str, Callable[[], ModuleType]]:
    """
    Discover global plugins (i.e. plugins installed via `pip`).

    Returns
    -------
    A `Set` containing the plugin names.
    """
    return {
        entry_point.module: lambda: entry_point.load()
        for entry_point in metadata.entry_points(group=PLUGIN_ENTRY_POINT)
    }


def discover_plugins() -> (
    tuple[dict[str, Callable[[], ModuleType]], dict[str, Callable[[], ModuleType]]]
):
    """
    Discover all plugins for the application, with local plugins shadowing global plugins.

    Returns
    -------
    A tuple of (local plugins, global plugins). Each entry in the tuple is a mapping of plugin
    names to a function that will import the plugin.
    """
    local_plugins = discover_local_plugins()
    global_plugins = discover_global_plugins()

    # remove duplicate names from the global plugins
    for plugin_name in set(local_plugins).intersection(global_plugins):
        # not using a default because the keys must be in the dictionary
        global_plugins.pop(plugin_name)

    return (local_plugins, global_plugins)


def load_plugin_settings(file: PathLike[str] | str, plugins: Iterable[str]) -> dict[str, bool]:
    """
    Load plugin settings, removing entries for non-installed plugins and adding entries for newly
    installed plugins.

    Parameters
    ----------
    file
        The JSON file containing the plugin settings.
    plugins
        The discovered plugin names.

    Returns
    The plugin settings.
    """
    try:
        with open(file, "r") as f:
            plugin_settings = typing.cast(dict[str, bool], json.load(f))
        # only include plugins from **plugins**. If the file did not contain an entry for a plugin,
        # assume the plugin is enabled
        return {name: plugin_settings.pop(name, True) for name in plugins}
    except Exception:  # if the file couldn't be loaded, all plugins are enabled
        logging.getLogger(__name__).info(
            f"Failed to read plugin settings file: {file}", exc_info=True
        )
        return {name: True for name in plugins}


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
        should_load = plugin_settings[plugin_name]
        if not should_load:
            continue  # don't load the plugin
        try:
            loaded_plugins[plugin_name] = loader_command()
        except Exception:
            logging.getLogger(__name__).exception(f"Error while loading plugin {plugin_name}")
            failed_plugins.append(plugin_name)

    return (loaded_plugins, failed_plugins)


def load_all_plugins() -> tuple[list[CategoryItem], list[QWidget]]:
    """
    Load all plugins.

    Returns
    -------
    The `CategoryItem`s and settings menu widgets loaded from plugins.
    """
    # discover plugins
    local_names, global_names = discover_plugins()
    # load plugin settings (i.e. if plugins are enabled or disabled)
    local_settings = load_plugin_settings(LOCAL_PLUGINS_FILE, local_names.keys())
    global_settings = load_plugin_settings(GLOBAL_PLUGINS_FILE, global_names.keys())
    # load the plugins
    local_plugins, failed_locals = load_plugins(local_names, local_settings)
    global_plugins, failed_globals = load_plugins(global_names, global_settings)
    # possibly report an error to the user
    message = ""
    if len(failed_locals) > 0:
        message += f"Failed to load local plugins:\n\n{", ".join(failed_locals)}\n\n"
    if len(failed_globals) > 0:
        message += f"Failed to load global plugins:\n\n{", ".join(failed_globals)}\n\n"
    if message != "":
        message += "See the error log for details."
        errors.show_error_delayed("Plugin Error", message)

    # load items from plugins
    items, failed_locals, failed_globals = sequence_builder.items_from_plugins(
        local_plugins, global_plugins
    )
    # possibly report an error to the user
    message = ""
    if len(failed_locals) > 0:
        message += f"Failed to load items from local plugins:\n\n{", ".join(failed_locals)}\n\n"
    if len(failed_globals) > 0:
        message += f"Failed to load items from global plugins:\n\n{", ".join(failed_globals)}\n\n"
    if message != "":
        message += "See the error log for details."
        errors.show_error_delayed("Plugin Items Error", message)

    # TODO: load settings widgets
    return (items, [])
