from typing import Self, Callable, Any
from PyQt6.QtWidgets import QLayout
from ....custom_widgets.container import FixedContainer

"""This widget is a base class and so does not have a corresponding data encoding."""


class BaseWidget(FixedContainer):
    """
    Base class for all linked widgets in the tree view.
    You must override:
    - `__init__()`: Call the base method.
    - `from_dict()`: Base method optional.
    - `to_dict()`: Base method optional.
    """

    def __init__(self, layout_fn: Callable[[], QLayout], display_name: str = ""):
        super().__init__(layout_fn)
        self.set_display_name(display_name)

    def set_display_name(self, display_name: str):
        """(private method) Set the text displayed on the window."""
        self.setWindowTitle(display_name)

    def display_name(self) -> str:
        """Get the text displayed on the window."""
        return self.windowTitle()

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        """
        Create a widget from a JSON-style dictionary.

        :param data_as_dict: A dictionary representing the widget's data in JSON format.
        """
        return cls(QLayout)

    def to_dict(self) -> dict:
        """
        Convert all of this item's data into a JSON-like dictionary. The base method returns an
        empty dictionary.
        """
        return dict()


class CategoryWidget:
    """
    Fake widget class for category items (i.e. non-sequence items). You must override:
    - `DISPLAY_NAME`
    """

    DISPLAY_NAME = ""

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
        return self.DISPLAY_NAME

    def set_display_name(self, display_name: str):
        pass
