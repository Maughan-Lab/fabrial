import json
import os
from typing import Any

from .. import Files

CATEGORY_FILENAME = "category.json"
ERROR_PREFIX = "Could not parse initialization directory:"


def item_dict_from_directory(directory: str) -> dict[str, Any]:
    """
    Build a TreeItem-friendly dictionary from a properly formatted directory. This main use of this
    function is for constructing a TreeModel from the application's item initialization directory.

    # The Format
    This function interprets folders as categories. Folders may contain other folders to nest
    categories. Every folder must contain a **category.json** file which initializes the category.

    Files are interpreted as entries in a category. Every .json file must contain a **type** entry.
    The **widget data** entry is optional if the widget has no data, and the **children** entry will
    be ignored (since the category's children will be determined from the file structure).

    The only file name that matters is **category.json**; every other item is defined by the
    contents of the file, not the name.

    Finally, items in the output dictionary appear in an arbitrary order, so must be sorted manually
    if order matters.

    # Exceptions
    This will throw a **FileNotFoundError** if 1) the directory does not contain a category.json
    file, or 2) the directory does not contain any item files.

    :param directory: The base directory to start the build process from.
    :returns: The dictionary created by parsing **directory**.
    """
    # get the name of a file in the directory and all folders
    item_as_dict: dict[str, Any]
    children: list[dict] = list()
    category_file_found = False

    for filename in os.listdir(directory):
        real_filename = os.path.join(directory, filename)
        if os.path.isdir(real_filename):  # it is a subcategory of the category
            children.append(item_dict_from_directory(real_filename))
        elif os.path.isfile(real_filename):
            with open(real_filename, "r") as f:
                item_data = json.load(f)
            if Files.TreeItem.WIDGET_DATA not in item_data:  # widget data is optional
                item_data[Files.TreeItem.WIDGET_DATA] = dict()
            if filename == CATEGORY_FILENAME:  # it is the category item
                category_file_found = True
                item_as_dict = item_data
            else:  # it is a child of the category item
                item_data[Files.TreeItem.CHILDREN] = dict()  # ignore children entries
                children.append(item_data)

    if not category_file_found:
        # you must have a category.json file
        raise FileNotFoundError(f"{ERROR_PREFIX} {CATEGORY_FILENAME} file not found in {directory}")

    # put the subitems in the current item
    item_as_dict[Files.TreeItem.CHILDREN] = children

    return item_as_dict
