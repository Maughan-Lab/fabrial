"""This widget is a null class and so does not have a corresponding data encoding."""

from typing import Self


class NullWidget:
    """Empty class for the root of a tree model."""

    def __init__(self):
        self.display_name = ""

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict) -> Self:
        return cls()

    def to_dict(self) -> dict:
        return dict()

    def show(self):  # there is nothing to show
        pass
