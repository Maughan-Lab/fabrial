from __future__ import annotations

import logging
from dataclasses import dataclass, field
from types import ModuleType
from typing import Iterable, Mapping, MutableMapping

from ..sequence_builder import CategoryItem, DataItem, SequenceItem, TreeItem


@dataclass
class CategoryInfo:
    """Container used internally by the application. This is not for plugins."""

    items: list[SequenceItem]
    subcategories: dict[str, CategoryInfo]


@dataclass
class PluginCategory:
    """Container that represents an item category from a plugin."""

    name: str
    items: Iterable[DataItem]
    subcategories: Iterable[PluginCategory] = field(default_factory=list)


def items_from_plugins(
    plugin_modules: Mapping[str, ModuleType],
) -> tuple[list[CategoryItem], list[str], list[str]]:
    """
    Helper function for `OptionsModel.from_plugins()`.

    Creates a list of `CategoryItem`s from a group of plugins. Logs errors.

    Returns
    -------
    A tuple of (the created `CategoryItem`s, any plugins that couldn't be loaded, any categories
    that couldn't be loaded).
    """

    failure_plugins: list[str] = []
    failure_categories: list[str] = []

    # helper function to parse plugin categories into the `category_info_map`. This function can
    # fail, so it must be wrapped in a try/except block
    def parse_plugin_categories(
        plugin_categories: Iterable[PluginCategory],
        category_info_map: MutableMapping[str, CategoryInfo],
    ):
        for plugin_category in plugin_categories:
            # get or create the combined category
            try:
                category_info = category_info_map[plugin_category.name]
            except KeyError:
                category_info = CategoryInfo([], {})
                category_info_map[plugin_category.name] = category_info
            # add the plugin's items (after building them into `SequenceItem`s)
            category_info.items.extend(
                [SequenceItem(None, data_item) for data_item in plugin_category.items]
            )
            # parse subcategories (recursive)
            parse_plugin_categories(plugin_category.subcategories, category_info.subcategories)

    # helper function to parse the category info map into actual `CategoryItem`s
    def parse_into_items(category_info_map: dict[str, CategoryInfo]) -> list[CategoryItem]:
        category_items: list[CategoryItem] = []
        for category_name, category_info in sorted(category_info_map.items()):
            try:
                # get the subcategory items (they will already be sorted)
                sub_category_items = parse_into_items(category_info.subcategories)  # recurse
                # sort the sequence items
                category_info.items.sort(key=lambda item: item.display_name())
                # combine the subcategory items and sequence items
                items: list[TreeItem] = []
                items.extend(sub_category_items)
                items.extend(category_info.items)
                # create and append the `CategoryItem`
                category_items.append(CategoryItem(None, category_name, items))
            except Exception:
                logging.getLogger(__name__).exception(
                    "Exception while parsing `CategoryInfo`s into `CategoryItem`s"
                )
                failure_categories.append(category_name)

        return category_items

    category_info_map: dict[str, CategoryInfo] = {}
    for name, plugin_module in plugin_modules.items():
        try:
            # PLUGIN.categories() is a mandatory entry point for plugins
            plugin_categories: list[PluginCategory] = plugin_module.categories()
            parse_plugin_categories(plugin_categories, category_info_map)
        except Exception:
            logging.getLogger(__name__).exception(
                "Exception while parsing plugin categories into `CategoryInfo`s"
            )
            failure_plugins.append(name)

    return (parse_into_items(category_info_map), failure_plugins, failure_categories)
