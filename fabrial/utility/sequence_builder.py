from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, MutableMapping
from dataclasses import dataclass, field
from types import ModuleType

from ..sequence_builder import CategoryItem, DataItem, SequenceItem, TreeItem


@dataclass
class CategoryInfo:
    """Container used internally by the application. This is not for plugins."""

    items: list[SequenceItem]
    subcategories: dict[str, CategoryInfo]  # {category name: category info}


@dataclass
class PluginCategory:
    """Container that represents an item category from a plugin."""

    name: str
    items: Iterable[DataItem]
    subcategories: Iterable[PluginCategory] = field(default_factory=list)


# the main function
def items_from_plugins(
    plugins: Mapping[str, ModuleType],
) -> tuple[list[CategoryItem], list[str]]:
    """
    Load `PluginCategory`s from **plugins**, then combine them all into a sorted list of
    `CategoryItem`s. Logs errors.

    Returns
    -------
    A tuple of (the loaded items, plugins items could not be loaded from).
    """
    failed_plugins: list[str] = []
    category_info_map: dict[str, CategoryInfo] = {}
    # extract the `PluginCategory`s from the plugins, then parse them into `CategoryInfo`s
    for plugin_name, plugin_module in plugins.items():
        try:
            plugin_categories: Iterable[PluginCategory] = plugin_module.categories()
            parse_plugin_categories(plugin_categories, category_info_map)
        except Exception:  # if we fail, log the error and skip this plugin
            logging.getLogger(__name__).exception(
                f"Error while loading items from plugin {plugin_name}"
            )
            failed_plugins.append(plugin_name)
            continue  # skip
    # finally, parse the `CategoryInfo`s into `CategoryItem`s
    return (parse_into_items(category_info_map), failed_plugins)


def parse_plugin_categories(
    plugin_categories: Iterable[PluginCategory],
    category_info_map: MutableMapping[str, CategoryInfo],
):
    """
    Parse the `PluginCategories` in **plugin_categories** into `CategoryInfo`s by updating
    **category_info_map**.
    """
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
    """Parse the input `CategoryInfo`s into a list of sorted `CategoryItem`s."""
    category_items: list[CategoryItem] = []
    for category_name, category_info in sorted(category_info_map.items()):
        # get the subcategory items (they will already be sorted)
        sub_category_items = parse_into_items(category_info.subcategories)  # recurse
        # sort the sequence items by display name
        category_info.items.sort(key=lambda item: item.display_name())
        # combine the subcategory items and sequence items
        items: list[TreeItem] = []
        items.extend(sub_category_items)
        items.extend(category_info.items)
        # create and append the `CategoryItem`
        category_items.append(CategoryItem(None, category_name, items))

    return category_items
