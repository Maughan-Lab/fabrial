from typing import Union, Any
from . import Encoding
from enum import Enum
from .test_widget import TestWidget


class WidgetType(Enum):
    POTENTIOSTATIC_EIS = 0
    TEST = 1

    def to_class(self) -> type[TestWidget]:
        """Return a widget class."""
        match self:
            case WidgetType.POTENTIOSTATIC_EIS:
                return TestWidget
            case WidgetType.TEST:
                return TestWidget

    @staticmethod
    def from_class_object(class_object: object) -> "WidgetType":
        match class_object:
            case TestWidget():  # this does not create a new instance, so no wasted time!
                return WidgetType.TEST
        print("should have already returned, ERROR")
        return WidgetType.TEST


class TreeItem:
    """Class to represent items on a tree model."""

    def __init__(self, parent: Union["TreeItem", None], linked_widget: TestWidget):
        self.parent_item = parent
        self.linked_widget: TestWidget = linked_widget
        self.children: list["TreeItem"] = []

    def show_widget(self):
        if self.linked_widget is not None:
            self.linked_widget.show()

    def child(self, index: int) -> Union["TreeItem", None]:
        """Get the child item at **index**."""
        try:
            return self.children[index]
        except Exception:
            return None

    def parent(self):
        """Get the parent of this item."""
        return self.parent_item

    def child_count(self) -> int:
        """Get the number of child items."""
        return len(self.children)

    def child_index(self) -> int:
        """
        Get the index of this item in its parent's list of child items. If this object has no
        parent, return 0.
        """
        if self.parent_item is not None:
            return self.parent_item.children.index(self)
        return 0

    def name(self) -> str:
        """Get the display text for this item."""
        # TODO: implement based off of the linked_widget's name
        return self.linked_widget.display_name

    def append_children(self, items: list["TreeItem"]):
        """Append all **items** to this item's list of children."""
        for item in items:
            self.children.append(item)

    def insert_children(self, starting_row_index: int, items: list["TreeItem"]) -> bool:
        """
        Insert **count** children starting at **starting_row_index**, with the newest children on
        top. Returns True if successful, False otherwise.
        """
        try:
            for i, item in enumerate(items):
                self.children.insert(starting_row_index + i, item)
        except Exception:
            return False
        return True

    def remove_children(self, starting_row_index: int, count: int) -> bool:
        """
        Remove **count** children starting at **starting_row_index**. Returns True if successful,
        False otherwise.
        """
        try:
            for _ in range(count):
                self.children.pop(starting_row_index)
        except Exception:
            return False
        return True

    @classmethod
    def from_dict(
        cls: type["TreeItem"], parent: Union["TreeItem", None], item_as_dict: dict[str, Any]
    ) -> "TreeItem":
        """
        Create a TreeItem from a JSON-style dictionary. This method is recursive.

        :param item_as_dict: A dictionary representing the item's data in JSON format.
        """
        widget_class = WidgetType(item_as_dict[Encoding.TreeItem.TYPE]).to_class()
        widget = widget_class.from_dict(item_as_dict[Encoding.TreeItem.DATA])

        # cls is the Class, TreeItem in this case. It is passed implicitly
        item = cls(parent, widget)

        for child_item_as_dict in item_as_dict[Encoding.TreeItem.CHILDREN]:
            child_item = cls.from_dict(item, child_item_as_dict)
            item.append_children([child_item])

        return item

    def to_dict(self) -> dict[str, Any]:
        """
        Convert all of this item's data into a JSON-like dictionary.
        """
        item_as_dict: dict[str, Any] = dict()  # empty dictionary
        # convert the widget type to a number
        item_as_dict[Encoding.TreeItem.TYPE] = WidgetType.from_class_object(
            self.linked_widget
        ).value
        # convert the widget data to a dictionary
        item_as_dict[Encoding.TreeItem.DATA] = self.linked_widget.to_dict()
        # recursively create a list of dictionaries representing each child
        item_as_dict[Encoding.TreeItem.CHILDREN] = [child.to_dict() for child in self.children]
        return item_as_dict
