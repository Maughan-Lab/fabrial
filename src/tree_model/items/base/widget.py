from typing import Self, Callable, Any
from PyQt6.QtWidgets import QLayout
from ....custom_widgets.container import Container

"""This widget is a base class and so does not have a corresponding data encoding."""


class BaseWidget(Container):
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
        """Set the text displayed on the window."""
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
