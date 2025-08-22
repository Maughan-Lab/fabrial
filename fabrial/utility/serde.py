"""
Utilities for serializing and deserializing objects. When deserializing, the object type is read
from the file.
"""

from __future__ import annotations

import json
import tomllib
import typing
from abc import abstractmethod
from collections.abc import Mapping, Sequence
from os import PathLike
from typing import Any, Protocol, Self

TYPE = "type"
DESERIALIZABLE_CLASSES: dict[str, type[Deserialize]] = {}

type Json = Mapping[str, Json] | Sequence[Json] | str | int | float | bool | None


class Deserialize(Protocol):
    """An object that can be deserialized without knowing the type ahead of time."""

    @classmethod
    @abstractmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:
        """Build the object from a JSON-like structure."""
        ...

    def __init_subclass__(cls):  # runs when `Deserialize` is subclasses
        typename = str(cls).split("'")[1]
        # ^
        # for example, str(int) gives "<class 'int'>", so we split on "'" to get
        # ["<class ", "int", ">"] and take the "int" part
        DESERIALIZABLE_CLASSES[typename] = cls  # store the type


class Serialize(Protocol):
    """An object that can be serialized into a type-tagged JSON dictionary."""

    @abstractmethod
    def serialize(self) -> dict[str, Json]:
        """Convert the object to a JSON-like structure. This method does not add a type tag."""
        ...

    def serialize_tagged(self) -> dict[str, Json]:
        """Serialize and add a type tag. This calls `serialize()`."""
        # str(TYPE) gives "<class 'TYPE'>" so we just extract the TYPE part
        type_tagged_dict: dict[str, Json] = {TYPE: str(type(self)).split("'")[1]}
        type_tagged_dict.update(self.serialize())
        return type_tagged_dict

    def save_json(self, file: PathLike[str] | str) -> bool:
        """Save the object to a JSON file. Returns whether the operation succeeded."""
        try:
            with open(file, "w") as f:
                json.dump(self.serialize_tagged(), f)
            return True
        except Exception:
            return False


def get_type(typename: str) -> type[Deserialize]:
    """Get a `Deserialize` subtype from a string representation."""
    try:
        return DESERIALIZABLE_CLASSES[typename]  # defined at the top of the file
    except KeyError:
        raise KeyError(f"`{typename}` does not represent a `Deserialize` object")


def deserialize(serialized_obj: Json) -> Any:
    """
    Deserialize **serialized_obj**. Any type-tagged dictionaries are deserialized into the
    corresponding `Deserialize` object.
    """

    # deserializes a dictionary
    def inner_deserialize_dict(item: Mapping[str, Json]) -> Any:
        try:
            # get the typename key
            typename = typing.cast(str, item[TYPE])  # cast assumes `typename` is `str`
        except KeyError:
            # if we got here the `item` dictionary is not a `Deserialize` object
            return {  # recurse into the rest of the dictionary and deserialize it
                inner_key: inner_deserialize_json(inner_item)
                for inner_key, inner_item in item.items()
            }
        # if we get here we have a type tag
        cls = get_type(typename)  # get the actual type
        # convert the dictionary into the actual `Deserialize` object
        return cls.deserialize(item)

    # deserializes a list
    def inner_deserialize_list(items: Sequence[Json]) -> Any:
        deserialized_items = []
        for inner_item in items:
            # replace each element in the list with its deserialized version
            deserialized_items.append(inner_deserialize_json(inner_item))
        # return the modified list
        return deserialized_items

    # helper function to recurse into JSON structures
    def inner_deserialize_json(item: Json) -> Any:
        # if the item is a dictionary, deserialize the dictionary
        if isinstance(item, dict):
            return inner_deserialize_dict(item)
        # if the item is a list, deserialize the list
        elif isinstance(item, list):
            return inner_deserialize_list(item)
        # otherwise the item is primitive, don't deserialize
        else:
            return item

    return inner_deserialize_json(serialized_obj)


def load_json(file: PathLike[str] | str) -> Any:
    """
    Load an object from a JSON file. Any type-tagged dictionaries are deserialized into the
    corresponding `Deserialize` object.
    """
    with open(file, "r") as f:
        object_as_dict = json.load(f)
    return deserialize(object_as_dict)


def load_toml(file: PathLike[str] | str) -> Any:
    """
    Load an object from a TOML file. Any type-tagged dictionaries are deserialized into the
    corresponding `Deserialize` object.
    """
    with open(file, "rb") as f:
        object_as_dict = tomllib.load(f)
    return deserialize(object_as_dict)
