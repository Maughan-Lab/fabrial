from __future__ import annotations

import importlib
import os
import pkgutil
import tomllib
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from types import ModuleType
from typing import Iterable

from .. import plugins
from ..constants import paths
from ..sequence_builder import DataItem
from ..sequence_builder.tree_items import CategoryItem, SequenceItem, TreeItem
from ..utility import serde

FILE_EXTENSION = ".toml"
CATEGORY_FILENAME = "category" + FILE_EXTENSION
NAME = "name"


@dataclass
class Category:
    items: list[SequenceItem]
    subcategories: dict[str, Category]


def items_from_directories(
    directories: Iterable[Path],
) -> tuple[list[CategoryItem], list[Path]]:
    """
    Helper function for `OptionsModel.from_directory()`.

    Creates an iterable of `CategoryItem`s from a group of properly formatted directories.

    Returns
    -------
    A tuple of

        (the created `CategoryItem`s, the `Path`s of any directories or files that could not be
        parsed)

    Raises
    ------
    ValueError
        A category file has the wrong contents.

    Also any errors from `serde.load_toml()`.

    The Format
    ----------
    ```
    base
    ├── category1
    │   ├── category.toml
    │   ├── item1.toml
    │   └── toml2.toml
    └── category2
        ├── category.toml
        ├── item1.toml
        └── toml2.toml
    ```
    An example structure is shown above. Folders containing a `category.toml` file are
    interpreted as categories. All item files in the folder are grouped under the same category
    defined by the `category.toml` file. Item files can be named anything other than
    `category.toml`, for example `item.toml`.

    Notes
    -----
    - Item files' names are unimportant; they only need to have the `.toml` extension and the right
    file contents.

    - Non-`TOML` files are ignored.

    - Files in directories without a category file are ignored, but nested directories are checked
    for categories.

    - You can nest categories by putting category directories inside other category directories.

    - Categories and their contained items are all sorted alphabetically by display name after
    being loaded. Subcategories are first, followed by sequence items.
    """

    failure_paths: dict[Path, Exception] = {}

    # helper function to read individual directories recursively
    def parse_directory(directory: Path, category_map: dict[str, Category]):
        _, subdirectories, files = next(os.walk(directory))

        category_file = directory.joinpath(CATEGORY_FILENAME)
        if category_file.exists():  # this folder is a category
            # read the category file
            try:
                with open(category_file, "rb") as f:
                    category_info = tomllib.load(f)
                # get the category name
                try:
                    category_name: str = category_info[NAME]
                    assert isinstance(category_name, str)  # it must be a `str`
                except KeyError:
                    raise KeyError(f"No `{NAME}` field in category file {category_file}")
            except Exception as e:
                failure_paths[directory] = e
                return  # don't keep parsing
            # get or create the category
            try:
                category = category_map[category_name]
            except KeyError:
                category = Category([], {})
                category_map[category_name] = category
            # parse subdirectories
            for subdirectory in subdirectories:
                subdirectory_path = directory.joinpath(subdirectory)
                parse_directory(subdirectory_path, category.subcategories)  # recurse
            # parse item files
            for file in files:
                file_path = directory.joinpath(file)
                # ignore non-item files and the category file
                if file_path.suffix != FILE_EXTENSION or file_path.name == CATEGORY_FILENAME:
                    continue

                # load the `DataItem` and build the `SequenceItem`
                try:
                    data_item = serde.load_toml(file_path)
                    if not isinstance(data_item, DataItem):
                        raise TypeError(
                            f"Loading the item file {file_path} yielded a non-`DataItem`"
                        )
                except Exception as e:
                    failure_paths[file_path] = e
                    continue  # stop parsing this file
                sequence_item = SequenceItem(None, data_item)
                # insert the item so the list is sorted
                category.items.append(sequence_item)
        else:  # this folder is not a category; recurse into other directories
            for subdirectory in subdirectories:
                subdirectory_path = directory.joinpath(subdirectory)
                parse_directory(subdirectory_path, category_map)  # use the current category map

    # helper function to parse the category map into actual `CategoryItem`s
    def parse_into_items(category_map: dict[str, Category]) -> list[CategoryItem]:
        category_items: list[CategoryItem] = []
        for category_name, category in sorted(category_map.items()):
            # get the subcategory items (they will already be sorted)
            sub_category_items = parse_into_items(category.subcategories)  # recurse
            # sort the sequence items
            category.items.sort(key=lambda item: item.get_display_name())
            # combine the subcategory items and sequence items
            items: list[TreeItem] = []
            items.extend(sub_category_items)
            items.extend(category.items)
            # create and append the `CategoryItem`
            category_items.append(CategoryItem(None, category_name, items))

        return category_items

    # parse the directories
    category_map: dict[str, Category] = {}
    for directory in directories:
        parse_directory(directory, category_map)

    # create the `CategoryItem`s
    # TODO: log the errors in the error log file
    return (parse_into_items(category_map), list(failure_paths.keys()))


def load_local_plugins() -> dict[str, ModuleType]:
    """Load plugins from the `plugins` directory."""
    plugin_modules: dict[str, ModuleType] = {}
    # search for packages in the `plugins` directory
    for _, name, is_package in pkgutil.iter_modules(plugins.__path__):
        if not is_package:  # ignore non packages
            continue
        try:
            module = importlib.import_module("." + name, plugins.__name__)
            plugin_modules[name] = module
        except Exception:
            # TODO: log error
            # TODO: add module to the list of packages that failed
            continue
    return plugin_modules


def load_plugins() -> list[ModuleType]:
    """Load plugins for the application."""
    plugin_modules = load_local_plugins()

    # TODO: load pip installed plugins

    return list(plugin_modules.values())


def get_initialization_directories(plugin_modules: Iterable[ModuleType]) -> list[Path]:
    """
    Get the application's item initialization directories. This includes items from any plugins.
    """

    initialization_directories: list[Path] = []

    for plugin_module in plugin_modules:
        try:
            directories = plugin_module.get_item_directories()
            assert isinstance(directories, list)
            initialization_directories.extend(directories)
        except AttributeError:  # the plugin doesn't have this entry point, skip
            continue
        except AssertionError:  # the entry point returned the wrong type, skip
            continue

    # TODO: figure out a scheme for communicating which plugins were bad

    return [paths.sequence_builder.OPTIONS_INITIALIZERS] + initialization_directories
