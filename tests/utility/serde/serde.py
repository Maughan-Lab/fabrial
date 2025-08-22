import json
import os
import typing
from collections.abc import Generator, Mapping
from pathlib import Path
from typing import Self

from pytest import fixture

from fabrial.utility import serde
from fabrial.utility.serde import TYPE, Deserialize, Json, Serialize

TYPENAME = "tests.utility.serde.serde.MockSerde"
FILES_DIRECTORY = Path(__file__).parent.joinpath("files")


class MockSerde(Deserialize, Serialize):
    """Test class that implements `Deserialize` and `Serialize`."""

    def __init__(self, number: int):
        self.number = number

    @classmethod
    def deserialize(cls, serialized_obj: Mapping[str, Json]) -> Self:
        return cls(typing.cast(int, serialized_obj["number"]))

    def serialize(self) -> dict[str, Json]:
        return {"number": self.number}

    def __eq__(self, other: Self):  # type: ignore
        return self.number == other.number


def test_get_type():
    """Tests `serde.get_type()`."""
    assert serde.get_type(TYPENAME) == MockSerde


@fixture
def number() -> int:
    """Fixture to generate the number used by mock objects."""
    return 50


@fixture
def mock_object(number: int) -> MockSerde:
    """Fixture to generate a mock `Serialize`/`Deserialize` object."""
    return MockSerde(number)


def test_deserialize(mock_object: MockSerde, number: int):
    """Tests `serde.deserialize()`."""
    # primitive case
    assert serde.deserialize(47) == 47
    # simple case
    simple_deserializable: dict[str, Json] = {"type": TYPENAME, "number": number}
    assert serde.deserialize(simple_deserializable) == mock_object
    # nested case
    nested_obj: dict[str, Json] = {
        "random_thing": 47,
        "actual_item": {"type": TYPENAME, "number": number},
    }
    assert serde.deserialize(nested_obj) == {"random_thing": 47, "actual_item": mock_object}
    # list case
    list_obj: list[Json] = ["something", 47, {"type": TYPENAME, "number": number}]
    assert serde.deserialize(list_obj) == ["something", 47, mock_object]
    # nested list and dict case
    complex_obj: dict[str, Json] = {
        "random_thing": 47,
        "list": [47, "something", {"type": TYPENAME, "number": number}],
        "nested": {
            "list": [47, "something", {"type": TYPENAME, "number": number}],
            "item": {"type": TYPENAME, "number": number},
        },
    }
    assert serde.deserialize(complex_obj) == {
        "random_thing": 47,
        "list": [47, "something", mock_object],
        "nested": {"list": [47, "something", mock_object], "item": mock_object},
    }


@fixture
def expected_load(mock_object: MockSerde) -> dict[str, int | MockSerde]:
    """Fixture for the expected result of loading from a file."""
    return {"random_thing": 47, "item": mock_object}


def test_load_toml(expected_load: dict[str, int | MockSerde]):
    """Tests `serde.load_toml()`."""
    file = FILES_DIRECTORY.joinpath("load_toml.toml")
    assert serde.load_toml(file) == expected_load


def test_load_json(expected_load: dict[str, int | MockSerde]):
    """Tests `serde.load_json()`."""
    file = FILES_DIRECTORY.joinpath("load_json.json")
    assert serde.load_json(file) == expected_load


@fixture
def save_json_file() -> Generator[Path, None, None]:
    """
    Fixture to provide the path for `serde.test_save_json()` and remove the file after the test
    completes.
    """
    file = FILES_DIRECTORY.joinpath("temp.json")
    yield file
    os.remove(file)  # remove the file when done


def test_save_json(save_json_file: Path):
    """Tests `serde.Serialize.save_json()`."""
    NUMBER = 500
    obj = MockSerde(NUMBER)
    obj.save_json(save_json_file)
    with open(save_json_file, "r") as f:
        assert json.load(f) == {TYPE: TYPENAME, "number": NUMBER}
