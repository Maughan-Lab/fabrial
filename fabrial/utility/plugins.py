from __future__ import annotations

import importlib
import logging
import pkgutil
from importlib import metadata
from types import ModuleType

from .. import plugins
from ..constants import PLUGIN_ENTRY_POINT


def load_plugins_from_module(module: ModuleType) -> tuple[dict[str, ModuleType], list[str]]:
    """
    Load plugins that are submodules of **module**.

    Returns
    -------
    A tuple of (the successfully loaded plugin modules, the modules that failed).
    """
    failure_plugins: list[str] = []
    plugin_modules: dict[str, ModuleType] = {}
    # search for packages in the `plugins` directory
    for _, name, is_package in pkgutil.iter_modules(module.__path__):
        if not is_package:  # ignore non packages
            continue
        try:
            plugin_module = importlib.import_module(module.__name__ + "." + name)
            plugin_modules[name] = plugin_module
        except Exception:
            logging.getLogger(__name__).exception(f"Failed to load local plugin {name}")
            failure_plugins.append(name)

    return (plugin_modules, failure_plugins)


def load_local_plugins() -> tuple[dict[str, ModuleType], list[str]]:
    """Load local plugins from the `plugins` directory."""
    # see `load_plugins_from_module()` for return value
    return load_plugins_from_module(plugins)


def load_global_plugins() -> tuple[dict[str, ModuleType], list[str]]:
    """
    Load plugins installed in the current Python environment (i.e. plugins installed with `pip`).

    Returns
    -------
    A tuple of (the successfully loaded plugin modules, the modules that failed).
    """
    failure_plugins: list[str] = []
    plugin_modules: dict[str, ModuleType] = {}
    for entry_point in metadata.entry_points(group=PLUGIN_ENTRY_POINT):
        name = entry_point.module
        try:
            plugin_modules[name] = entry_point.load()
        except Exception:
            logging.getLogger(__name__).exception(f"Failed to load global plugin {name}")
            failure_plugins.append(name)

    return (plugin_modules, failure_plugins)


def load_all_plugins() -> tuple[dict[str, ModuleType], list[str], list[str]]:
    """
    Load plugins for the application.

    Returns
    -------
    A tuple of (the successfully loaded plugin modules, the global plugins that failed, the local
    plugins that failed).

    Notes
    -----
    If any duplicate plugin names are found, the environment-installed (global) plugin is used.
    """
    local_plugin_modules, local_failure_plugins = load_local_plugins()
    global_plugin_modules, global_failure_plugins = load_global_plugins()

    plugin_modules = local_plugin_modules
    # fuse the plugin lists. If there are any duplicate plugin names, environment-installed plugin
    # is used
    plugin_modules.update(global_plugin_modules)

    return (plugin_modules, global_failure_plugins, local_failure_plugins)
