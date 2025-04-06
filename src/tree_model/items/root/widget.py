from typing import Self, Any


class NullWidget:
    """
    Empty class for the root of a tree model. This widget is a null class and so does not have a
    corresponding data encoding.
    """

    def __init__(self):
        pass

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        return cls()

    def to_dict(self) -> dict:
        return dict()

    def show(self):  # there is nothing to show
        pass

    def display_name(self) -> str:
        return ""

    def set_display_name(self, display_name: str):
        pass
