from __future__ import annotations

import importlib
import pkgutil

# from importlib import metadata
from types import ModuleType

from .. import plugins


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
            plugin_module = importlib.import_module("." + name, module.__name__)
            plugin_modules[name] = plugin_module
        except Exception as e:
            # TODO: log error
            e
            failure_plugins.append(name)
            continue
    return (plugin_modules, failure_plugins)


def load_local_plugins() -> tuple[dict[str, ModuleType], list[str]]:
    """Load plugins from the `plugins` directory."""
    return load_plugins_from_module(plugins)


def load_all_plugins() -> tuple[list[ModuleType], list[str]]:
    """Load plugins for the application."""
    plugin_modules, failure_plugins = load_local_plugins()

    # TODO: load pip installed plugins

    return (list(plugin_modules.values()), failure_plugins)
