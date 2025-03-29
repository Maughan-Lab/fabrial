"""This widget is a base class and so does not have a corresponding data encoding."""

from PyQt6.QtWidgets import QLayout
from typing import Self, Callable
from ...custom_widgets.container import Container


class BaseWidget(Container):
    """
    Base class for all linked widgets in the tree view. You must override the **__init__()**,
    **from_dict()**, and **to_dict()** methods, and the **DISPLAY_NAME** data member when
    subclassing. Additionally, you should use constants for each of the dictionary entries
    (put them in Encoding.py), and you need to update the **WidgetType** enumerator.
    """

    def __init__(self, layout_fn: Callable[[], QLayout]):
        super().__init__(layout_fn)
        self.display_name: str

    def set_display_name(self, display_name: str):
        self.display_name = display_name
        self.setWindowTitle(display_name)

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict) -> Self:
        """
        Create a widget from a JSON-style dictionary.

        :param data_as_dict: A dictionary representing the widget's data in JSON format.
        """
        return cls(QLayout)

    def to_dict(self) -> dict:
        """
        Convert all of this item's data into a JSON-like dictionary.
        """
        return dict()
