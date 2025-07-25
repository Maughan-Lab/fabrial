from __future__ import annotations

import json
import tomllib
from abc import abstractmethod
from os import PathLike
from typing import Any, Protocol, Self

TYPE = "type"
deserializable_classes: dict[str, type[Deserialize]] = {}


class Deserialize(Protocol):
    """An object that can be deserialized from a dictionary."""

    @classmethod
    @abstractmethod
    def from_dict(cls, obj_dict: dict[str, Any]) -> Self:
        """Build the object from a `dict`."""
        ...

    def __init_subclass__(cls):  # runs when `Deserialize` is subclasses
        typename = str(cls).split("'")[1]
        # ^
        # for example, str(int) gives "<class 'int'>", so we split on "'" to get
        # ["<class ", "int", ">"] and take the "int" part
        deserializable_classes[typename] = cls  # store the type


class Serialize(Protocol):
    """An object that can be serialized to a dictionary."""

    @abstractmethod
    def as_dict(self) -> dict[str, Any]:
        """Convert the object to a dictionary. Call the base method and extent the result."""
        # str(TYPE) gives "<class 'TYPE'>" so we just extract the TYPE part
        return {TYPE: str(type(self)).split("'")[1]}


def get_type(typename: str) -> type[Deserialize]:
    """Get a `Deserialize` subtype from a string representation."""
    try:
        return deserializable_classes[typename]  # defined at top of file
    except KeyError:
        raise KeyError(f"`{typename}` does not represent a `Deserialize` object")


def deserialize(object_as_dict: dict[str, Any]) -> Any:
    """
    Deserialize `object_as_dict` into an object. Any dictionaries containing the key `type` are
    interpreted as `Deserialize` objects.
    """

    # called to deserialize a dictionary
    def inner_deserialize_dict(item: dict[str, Any]) -> Any:
        try:
            # get the typename key
            typename: str = item[TYPE]
        except KeyError:
            # if we got here the `item` dictionary is not a `Deserialize object`
            # recurse into the rest of the dictionary and deserialize it
            replace_dict_values(item)
            # return the modified dictionary
            return item
        # if we get here we have a value for `typename` so we can deserialize
        # get the actual type from a pre-created dictionary
        cls = get_type(typename)
        # recurse into the rest of the dictionary and deserialize it
        replace_dict_values(item)
        # convert the dictionary into the actual `Deserialize` object
        return cls.from_dict(item)

    # called to deserialize a list
    def inner_deserialize_list(item: list[dict[str, Any]]) -> Any:
        # all entries in a list must be dictionaries for JSON-like formats
        for i, inner_item in enumerate(item):
            # replace each element in the list with its deserialized version
            item[i] = inner_deserialize_dict(inner_item)
        # return the modified list
        return item

    # helper function to recurse into dictionaries
    def replace_dict_values(item: dict[str, Any]):
        for inner_key, inner_item in item.items():
            # if the item is a dictionary, deserialize the dictionary
            if isinstance(inner_item, dict):
                item[inner_key] = inner_deserialize_dict(inner_item)
            # if the item is a list, deserialize the list
            elif isinstance(inner_item, list):
                item[inner_key] = inner_deserialize_list(inner_item)

    # we know the outer value from a JSON/TOML file will be a dictionary, so we start there
    return inner_deserialize_dict(object_as_dict)


def load_json(file: PathLike | str) -> Any:
    """Load a `Deserialize` object from a JSON file."""
    with open(file, "r") as f:
        object_as_dict = json.load(f)
    return deserialize(object_as_dict)


def save_json(file: PathLike | str, obj: Serialize) -> bool:
    """Save a `Serialize` object to a file."""
    try:
        object_as_dict = obj.as_dict()
        with open(file, "w") as f:
            json.dump(object_as_dict, f)
        return True
    except Exception:
        return False


def load_toml(file: PathLike | str) -> Any:
    """Load a `Deserialize` object from a TOML file."""
    with open(file, "rb") as f:
        object_as_dict = tomllib.load(f)
    return deserialize(object_as_dict)
