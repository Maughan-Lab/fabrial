from abc import ABC, ABCMeta, abstractmethod
from typing import Any, Self

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QLayout

from ...classes import AbstractBackgroundProcess, AbstractForegroundProcess, DescriptionInfo
from ...constants.tree_item import DEFAULT_ICON_FILENAME
from ...custom_widgets import ParameterDescriptionWidget
from ...utility import descriptions, images


class AbstractWidget(ABC):
    """
    Abstract class for sequence builder widgets.

    Parameters
    ----------
    layout
        The layout to use for the parameter tab.
    display_name
        The name displayed on the widget's item and window.
    process_type
        The type of the widget's associated `Process`.
    icon_filename
        The name of the icon file in the application's internal icon folder.
    description_info
        Information for setting the text of the description tab.
    supports_subitems
        Whether the associated item can have subitems.
    draggable
        Whether the associated item can be dragged.
    """

    def __init__(
        self,
        display_name: str = "",
        process_type: type[AbstractForegroundProcess | AbstractBackgroundProcess] | None = None,
        supports_subitems: bool = True,
        draggable: bool = False,
    ):
        self.linked_process_type = process_type
        self.item_supports_subitems = supports_subitems
        self.draggable = draggable
        self.set_display_name(display_name)

    @classmethod
    @abstractmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        """
        Create a widget from a JSON-style dictionary.

        Parameters
        ----------
        data_as_dict
            A dictionary representing the widget's data in JSON format.
        """
        raise TypeError(f"You must implement 'from_dict()' for {cls.__name__}.")

    def to_dict(self) -> dict[str, Any]:
        """Convert all of this item's data into a JSON-like dictionary."""
        return dict()

    def show_widget(self, enabled: bool):
        """
        Show the widget.

        Parameters
        ----------
        enabled
            Whether the parameter tab should be enabled.
        """
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
    """Metaclass combining `ParameterDescriptionWidget` and `ABCMeta`."""


class AbstractBaseWidget(ParameterDescriptionWidget, AbstractWidget, metaclass=ABCWidgetMeta):
    """
    Base class for all linked widgets in the tree view.
    You must override:
    - `from_dict()`
    - `to_dict()`

    Parameters
    ----------
    layout
        The layout to use for the parameter tab.
    display_name
        The name displayed on the widget's item and window.
    process_type
        The type of the widget's associated `Process`.
    icon_filename
        The name of the icon file in the application's internal icon folder.
    description_info
        Information for setting the text of the description tab.
    supports_subitems
        Whether the associated item can have subitems.
    """

    def __init__(
        self,
        layout: QLayout | None = None,
        display_name: str = "",
        process_type: type[AbstractForegroundProcess | AbstractBackgroundProcess] | None = None,
        icon_filename: str = DEFAULT_ICON_FILENAME,
        description_info: DescriptionInfo = DescriptionInfo(),
        supports_subitems: bool = False,
    ):
        ParameterDescriptionWidget.__init__(self, layout)
        AbstractWidget.__init__(self, display_name, process_type, supports_subitems, True)

        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowIcon(images.make_icon(icon_filename))
        self.set_description(descriptions.get_description(description_info))

    def show_widget(self, enabled: bool):
        self.parameter_widget().setEnabled(enabled)
        self.show()

    def display_name(self) -> str:
        return self.windowTitle()

    def set_display_name(self, display_name: str):
        self.setWindowTitle(display_name)

    def icon(self) -> QIcon:
        return self.windowIcon()

    def process_type(self) -> type[AbstractForegroundProcess | AbstractBackgroundProcess] | None:
        return self.linked_process_type

    def closeEvent(self, event: QCloseEvent | None):  # overridden
        if event is not None:
            # this makes sure show() has the parameter tab enabled
            self.parameter_widget().setEnabled(True)
        ParameterDescriptionWidget.closeEvent(self, event)


class CategoryWidget(AbstractWidget):
    """
    Fake widget class for category items (i.e. non-sequence items).

    Parameters
    ----------
    display_name
        The text to display on the item.
    """

    def __init__(self, display_name: str = ""):
        AbstractWidget.__init__(self, display_name)
        self.collapsed_icon = images.make_icon("folder-horizontal.png")
        self.expanded_icon = images.make_icon("folder-horizontal-open.png")
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
