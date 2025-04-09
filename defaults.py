import os
from typing import Any
import json

base_directory = "initialization"
TYPE = "type"
WIDGET_DATA = "linked-widget-data"
CHILDREN = "children"


def build(directory: str) -> dict[str, Any]:
    # get the name of a file in the directory and all folders
    item_file: str
    subdirectories: list[str] = []
    for filename in os.listdir(directory):
        real_filename = os.path.join(directory, filename)
        if os.path.isdir(real_filename):
            subdirectories.append(real_filename)
        elif os.path.isfile(real_filename):
            item_file = real_filename

    with open(item_file, "r") as f:
        item_as_dict: dict[str, Any] = json.load(f)

    # widget data is optional for items with no data
    if WIDGET_DATA not in item_as_dict:
        item_as_dict[WIDGET_DATA] = dict()
    # children are not included in the default files
    item_as_dict[CHILDREN] = list()

    children: list[dict] = item_as_dict[CHILDREN]
    for subdirectory in subdirectories:
        children.append(build(subdirectory))

    return item_as_dict


json.dump(build(base_directory), open("output.json", "w"))
