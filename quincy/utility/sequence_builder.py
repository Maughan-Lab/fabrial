from __future__ import annotations

import bisect
import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

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
                    data_item: DataItem = serde.load_toml(file_path)
                except Exception as e:
                    failure_paths[file_path] = e
                    continue  # stop parsing this file
                sequence_item = SequenceItem(None, data_item)
                # insert the item so the list is sorted
                bisect.insort_right(
                    category.items, sequence_item, key=lambda item: item.get_display_name()
                )
        else:  # this folder is not a category; recurse into other directories
            for subdirectory in subdirectories:
                subdirectory_path = directory.joinpath(subdirectory)
                parse_directory(subdirectory_path, category_map)  # use the current category map

    # helper function to parse the category map into actual `CategoryItem`s
    def parse_into_items(category_map: dict[str, Category]) -> list[CategoryItem]:
        category_items: list[CategoryItem] = []
        for category_name, category in sorted(category_map.items()):
            # get the subcategory items
            sub_category_items = parse_into_items(category.subcategories)  # recurse
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


def get_initialization_directories() -> Iterable[Path]:
    """
    Get the application's item initialization directories. This includes items from any plugins.
    """
    return [paths.sequence_builder.OPTIONS_INITIALIZERS]
