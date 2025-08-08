import os
import tomllib
from os import PathLike
from pathlib import Path
from typing import Iterable, Sequence

from ..constants import paths
from ..sequence_builder import DataItem
from ..sequence_builder.tree_items import CategoryItem, SequenceItem
from ..utility import serde

FILE_EXTENSION = ".toml"
CATEGORY_FILENAME = "category" + FILE_EXTENSION
NAME = "name"


def items_from_directories(
    directories: Iterable[PathLike[str] | str],
) -> Sequence[CategoryItem]:
    """
    Helper function for `OptionsModel.from_directory()`.

    Creates an iterable of `CategoryItem`s from a group of properly formatted directories.

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
    `category.toml`, for example `item.toml`. The file name is unimportant; only the contents
    matter. Non-TOML files are ignored. Categories are flattened; you cannot nest categories.

    Notes
    -----
    The categories and their contained items are all sorted alphabetically by display name after
    being loaded.
    """
    category_map: dict[str, list[SequenceItem]] = {}

    for directory in directories:
        for dir, _, files in os.walk(directory):
            dir_path = Path(dir)
            category_file = dir_path.joinpath(CATEGORY_FILENAME)
            # ignore directories that don't contain a category file
            if not category_file.exists():
                continue
            # initialize the category (if it hasn't already been initialized)
            with open(category_file, "rb") as f:
                category_info = tomllib.load(f)
            try:
                category_name: str = category_info[NAME]
            except KeyError:
                raise ValueError(f"No `{NAME}` field in category file {str(category_file)}")
            if category_name not in category_map:
                category_map[category_name] = []  # initialize with empty list

            for file in files:
                file_path = dir_path.joinpath(file)
                # ignore non-item files and the category file
                if file_path.suffix != FILE_EXTENSION or file_path.name == CATEGORY_FILENAME:
                    continue
                # load the `DataItem` and build the `SequenceItem`, then append it to the category
                data_item: DataItem = serde.load_toml(file_path)
                sequence_item = SequenceItem(None, data_item)
                category_map[category_name].append(sequence_item)

    # create the category items
    category_items: list[CategoryItem] = []
    # sort the categories alphabetically before iterating
    for category_name, sequence_items in sorted(category_map.items()):
        # sort all `SequenceItem`s by display name
        sequence_items.sort(key=lambda item: item.get_display_name())
        # create and append the `CategoryItem`
        category_items.append(CategoryItem(None, category_name, sequence_items))

    return category_items


def get_initialization_directories() -> Iterable[Path]:
    """
    Get the application's item initialization directories. This includes items from any plugins.
    """
    return [paths.sequence_builder.OPTIONS_INITIALIZERS]
