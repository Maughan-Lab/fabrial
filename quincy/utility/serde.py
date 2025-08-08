from __future__ import annotations

import json
import tomllib
from abc import abstractmethod
from os import PathLike
from typing import Any, Mapping, Protocol, Self, Sequence

TYPE = "type"
DESERIALIZABLE_CLASSES: dict[str, type[Deserialize]] = {}

type Json = dict[str, Json] | list[Json] | str | int | float | bool | None


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
    """An object that can be serialized and store the type."""

    @abstractmethod
    def serialize(self) -> dict[str, Json]:
        """
        Convert the object to a JSON-like structure. You must call the base method and extent the
        result.
        """
        # str(TYPE) gives "<class 'TYPE'>" so we just extract the TYPE part
        return {TYPE: str(type(self)).split("'")[1]}

    def save_json(self, file: PathLike[str] | str) -> bool:
        """Save the object to a JSON file. Returns whether the operation succeeded."""
        try:
            with open(file, "w") as f:
                json.dump(self.serialize(), f)
            return True
        except Exception:
            return False


def get_type(typename: str) -> type[Deserialize]:
    """Get a `Deserialize` subtype from a string representation."""
    try:
        return DESERIALIZABLE_CLASSES[typename]  # defined at top of file
    except KeyError:
        raise KeyError(f"`{typename}` does not represent a `Deserialize` object")


def deserialize(serialied_obj: Any) -> Any:
    """
    Deserialize `serialized_obj` into an object. Any dictionaries containing the key `type` are
    interpreted as `Deserialize` objects.
    """
    # TODO: better type annotations using Json

    # deserializes a dictionary
    def inner_deserialize_dict(item: Mapping[str, Any]) -> Any:
        try:
            # get the typename key
            typename: str = item[TYPE]
        except KeyError:
            # if we got here the `item` dictionary is not a `Deserialize object`
            # recurse into the rest of the dictionary and deserialize it
            return replace_dict_values(item)
        # if we get here we have a value for `typename` so we can deserialize
        # get the actual type from a pre-created dictionary
        cls = get_type(typename)
        # recurse into the rest of the dictionary and deserialize it, then
        # convert the dictionary into the actual `Deserialize` object
        return cls.deserialize(replace_dict_values(item))

    # deserializes a list
    def inner_deserialize_list(items: Sequence[dict[str, Any]]) -> Any:
        # all entries in a list must be dictionaries for JSON-like formats
        deserialized_items: list[Any] = []
        for inner_item in items:
            # replace each element in the list with its deserialized version
            deserialized_items.append(inner_deserialize_json(inner_item))
        # return the modified list
        return deserialized_items

    # helper function to recurse into dictionaries
    def replace_dict_values(item: Mapping[str, Any]) -> Mapping[str, Any]:
        return {
            inner_key: inner_deserialize_json(inner_item) for inner_key, inner_item in item.items()
        }

    # helper function to recurse into JSON structures
    def inner_deserialize_json(item: Any) -> Any:
        # if the item is a dictionary, deserialize the dictionary
        if isinstance(item, dict):
            return inner_deserialize_dict(item)
        # if the item is a list, deserialize the list
        elif isinstance(item, list):
            return inner_deserialize_list(item)
        # otherwise the item is primitive, don't deserialize
        else:
            return item

    return inner_deserialize_json(serialied_obj)


def load_json(file: PathLike[str] | str) -> Any:
    """Load an object from a JSON file. Any `Deserialize` objects are deserialized."""
    with open(file, "r") as f:
        object_as_dict = json.load(f)
    return deserialize(object_as_dict)


def load_toml(file: PathLike[str] | str) -> Any:
    """Load an object from a TOML file. Any `Deserialize` objects are deserialized."""
    with open(file, "rb") as f:
        object_as_dict = tomllib.load(f)
    return deserialize(object_as_dict)
