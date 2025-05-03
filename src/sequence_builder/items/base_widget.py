from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Self

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QLayout

from ... import Files
from ...classes.descriptions import DescriptionInfo
from ...classes.process import AbstractBackgroundProcess, AbstractForegroundProcess
from ...custom_widgets.parameter_description import ParameterDescriptionWidget
from ...utility.descriptions import get_description
from ...utility.images import make_icon


class AbstractWidget(ABC):
    """Abstract class for sequence builder widgets."""

    def __init__(
        self,
        display_name: str = "",
        process_type: type[AbstractForegroundProcess | AbstractBackgroundProcess] | None = None,
        supports_subitems: bool = True,
        draggable: bool = False,
    ):
        """
        :param layout: The layout to use for the parameter tab.
        :param display_name: The name displayed on the widget's item and window.
        :param process_type: The type of the widget's associated **Process**.
        :param icon_filename: The name of the icon file in the application's internal icon folder.
        :param description_info: Information for setting the text of the description tab.
        :param supports_subitems: Whether the associated item can have subitems.
        :param draggable: Whether the associated item can be dragged.
        """
        super().__init__()
        self.linked_process_type = process_type
        self.item_supports_subitems = supports_subitems
        self.draggable = draggable
        self.set_display_name(display_name)

    @classmethod
    @abstractmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        """
        Create a widget from a JSON-style dictionary.

        :param data_as_dict: A dictionary representing the widget's data in JSON format.
        """
        raise TypeError(f"You must implement 'from_dict()' for {cls.__name__}.")

    def to_dict(self) -> dict[str, Any]:
        """Convert all of this item's data into a JSON-like dictionary."""
        return dict()

    def show(self):
        """Show the widget."""
        pass

    def show_disabled(self):
        """Show the widget with the parameter tab disabled."""
        pass

    @abstractmethod
    def display_name(self) -> str:
        """Get the text displayed on the window."""
        pass

    def set_display_name(self, display_name: str):
        """Set the text displayed on the window."""
        pass

    @abstractmethod
    def icon(self) -> QIcon:
        """Get the widget's icon."""
        pass

    @staticmethod
    def allowed_to_create() -> bool:
        """Whether this widget (and by extension its associated item) is allowed to be created."""
        return True

    def process_type(self) -> type[AbstractForegroundProcess | AbstractBackgroundProcess] | None:
        """Get the process type."""
        return None

    def supports_subitems(self) -> bool:
        """Whether the associated item supports subitems."""
        return self.item_supports_subitems

    def supports_dragging(self) -> bool:
        """Whether the associated item can be dragged."""
        return self.draggable

    def expand_event(self):
        """Handle the item being expanded."""
        pass

    def collapse_event(self):
        """Handle the item being collapsed."""
        pass


class ABCWidgetMeta(type(ParameterDescriptionWidget), ABCMeta):  # type: ignore
    """Metaclass combining **ParameterDescriptionWidget** and **ABCMeta**."""


class AbstractBaseWidget(ParameterDescriptionWidget, AbstractWidget, metaclass=ABCWidgetMeta):
    """
    Base class for all linked widgets in the tree view.
    You must override:
    - `from_dict()`
    - `to_dict()`
    """

    def __init__(
        self,
        layout: QLayout | None = None,
        display_name: str = "",
        process_type: type[AbstractForegroundProcess | AbstractBackgroundProcess] | None = None,
        icon_filename: str = Files.TreeItem.DEFAULT_ICON_FILENAME,
        description_info: DescriptionInfo = DescriptionInfo(),
        supports_subitems: bool = False,
    ):
        """
        :param layout: The layout to use for the parameter tab.
        :param display_name: The name displayed on the widget's item and window.
        :param process_type: The type of the widget's associated **Process**.
        :param icon_filename: The name of the icon file in the application's internal icon folder.
        :param description_info: Information for setting the text of the description tab.
        :param supports_subitems: Whether the associated item can have subitems.
        """
        ParameterDescriptionWidget.__init__(self, layout)
        AbstractWidget.__init__(self, display_name, process_type, supports_subitems, True)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowIcon(make_icon(icon_filename))
        self.set_description(get_description(description_info))

    def show_disabled(self):
        self.parameter_widget().setDisabled(True)
        self.show()

    def display_name(self) -> str:
        return self.windowTitle()

    def set_display_name(self, display_name: str):
        self.setWindowTitle(display_name)

    def icon(self) -> QIcon:
        return self.windowIcon()

    def process_type(self) -> type[AbstractForegroundProcess | AbstractBackgroundProcess] | None:
        return self.linked_process_type


class CategoryWidget(AbstractWidget):
    """Fake widget class for category items (i.e. non-sequence items)."""

    def __init__(self, display_name: str = ""):
        """:param display_name: The text to display on the item."""
        super().__init__(display_name)
        self.collapsed_icon = make_icon("folder-horizontal.png")
        self.expanded_icon = make_icon("folder-horizontal-open.png")
        self.display_icon = self.collapsed_icon
        self.name = display_name

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        return cls()

    def display_name(self) -> str:
        return self.name

    def icon(self) -> QIcon:
        return self.display_icon

    def expand_event(self):
        self.display_icon = self.expanded_icon

    def collapse_event(self):
        self.display_icon = self.collapsed_icon
