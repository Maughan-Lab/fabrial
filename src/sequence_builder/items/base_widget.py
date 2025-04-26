from typing import Self, Any
from PyQt6.QtWidgets import QLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from ...custom_widgets.parameter_description import ParameterDescriptionWidget
from ...utility.images import make_icon
from ...classes.process import Process, BackgroundProcess


class BaseWidget(ParameterDescriptionWidget):
    """
    Base class for all linked widgets in the tree view.
    You must override:
    - `PROCESS_TYPE`

    - `__init__()`: Call the base method.
    - `from_dict()`: Base method optional.
    - `to_dict()`: Base method optional.

    You can also override `ICON` to change the item's icon. This parameter is the name of an icon
    file.
    """

    PROCESS_TYPE: type[Process] | type[BackgroundProcess] | None = None
    SUPPORTS_SUBITEMS: bool = False
    DRAGGABLE: bool = True
    ICON = "script.png"

    def __init__(self, layout: QLayout, display_name: str = ""):
        """
        :param layout: The layout to use for the parameter tab.
        :param display_name: The name displayed on the widget's item and window.
        """
        super().__init__(layout)
        self.set_display_name(display_name)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowIcon(make_icon(self.ICON))

    def show_disabled(self):
        """Show the widget with the parameter tab disabled."""
        self.parameter_widget().setDisabled(True)
        self.show()

    def display_name(self) -> str:
        """Get the text displayed on the window."""
        return self.windowTitle()

    def set_display_name(self, display_name: str):
        """Set the text displayed on the window."""
        self.setWindowTitle(display_name)

    def icon(self) -> QIcon:
        """Get the widget's icon."""
        return self.windowIcon()

    def expand_event(self):
        """(Virtual) Handle the item being expanded."""
        pass

    def collapse_event(self):
        """(Virtual) Handle the item being collapsed."""
        pass

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        """
        Create a widget from a JSON-style dictionary.

        :param data_as_dict: A dictionary representing the widget's data in JSON format.
        """
        return cls(QLayout())

    def to_dict(self) -> dict[str, Any]:
        """
        Convert all of this item's data into a JSON-like dictionary. The base method returns an
        empty dictionary.
        """
        return dict()


class CategoryWidget:
    """
    Fake widget class for category items (i.e. non-sequence items). You must override:
    - `DISPLAY_NAME`

    You can also override
    - `COLLAPSED_ICON` to change the icon used when the item is collapsed.
    - `EXPANDED_ICON` to change the icon used when the item is expanded.
    """

    PROCESS_TYPE = None
    SUPPORTS_SUBITEMS = True
    DRAGGABLE = False
    COLLAPSED_ICON = "folder-horizontal.png"
    EXPANDED_ICON = "folder-horizontal-open.png"

    DISPLAY_NAME = ""

    def __init__(self):
        self.collapsed_icon = make_icon(self.COLLAPSED_ICON)
        self.expanded_icon = make_icon(self.EXPANDED_ICON)
        self.display_icon = self.collapsed_icon

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        return cls()

    def to_dict(self) -> dict[str, Any]:
        return dict()

    def show(self):  # there is nothing to show
        pass

    def show_disabled(self):
        pass

    def display_name(self) -> str:
        return self.DISPLAY_NAME

    def set_display_name(self, display_name: str):  # display name is constant
        pass

    def icon(self) -> QIcon:
        return self.display_icon

    def expand_event(self):
        self.display_icon = self.expanded_icon

    def collapse_event(self):
        self.display_icon = self.collapsed_icon
