from __future__ import annotations

from functools import cmp_to_key
from typing import TYPE_CHECKING, Any, Union

from ..Files import TreeItem as Keys
from .items.base_widget import AbstractWidget, CategoryWidget
from .items.item_types import ItemType

if TYPE_CHECKING:
    from ..classes.process import AbstractBackgroundProcess, AbstractForegroundProcess


class TreeItem:
    """Class to represent items on a tree model."""

    def __init__(
        self,
        linked_widget: AbstractWidget,
        parent: TreeItem | None = None,
    ):
        self.parent_item = parent
        self.linked_widget = linked_widget
        self.children: list[TreeItem] = []
        self.running = False

    @classmethod
    def create_root_item(cls: type[TreeItem]):
        return cls(CategoryWidget())

    def set_running(self, running: bool):
        """Set whether this item's associated process is currently running."""
        self.running = running

    def is_running(self) -> bool:
        """Whether this item's associated process is currently running."""
        return self.running

    def show_widget(self, enabled: bool):
        """
        Show the linked widget in its own window.

        :param enabled: Whether the widget's parameters tab should be enabled.
        """
        self.linked_widget.show_widget(enabled)

    def widget(self) -> AbstractWidget:
        """Get the this item's linked widget."""
        return self.linked_widget

    def child(self, index: int) -> TreeItem | None:
        """Get the child item at **index**."""
        try:
            return self.children[index]
        except Exception:
            return None

    def parent(self) -> TreeItem | None:
        """Get the parent of this item."""
        return self.parent_item

    def child_count(self) -> int:
        """Get the number of child items."""
        return len(self.children)

    def has_children(self) -> bool:
        """Whether this item contains subitems."""
        return not self.child_count() == 0

    def subitems(self) -> list[TreeItem]:
        """Get this item's subitems."""
        return self.children

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
        return self.linked_widget.display_name()

    def append_children(self, items: list[TreeItem]):
        """Append all **items** to this item's list of children."""
        for item in items:
            self.children.append(item)

    def insert_children(self, starting_row_index: int, items: list[TreeItem]) -> bool:
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

    def sort_all(self):
        """
        Sort ALL of this item's children (i.e. children, grandchildren, etc.) by display name. Items
        containing other items are listed first.
        """

        def compare(left_item: TreeItem, right_item: TreeItem) -> int:
            """
            Compare two TreeItems. TreeItems with children take precedence. If both or neither have
            children, they are compared alphabetically by display name.
            """
            LEFT = -1
            RIGHT = 1
            EQUAL = 0
            if left_item.has_children():
                if not right_item.has_children():
                    return LEFT
                else:
                    if left_item.name() < right_item.name():
                        return LEFT
                    else:  # if the names are the same order doesn't matter
                        return RIGHT
            else:
                if right_item.has_children():
                    return RIGHT
                else:
                    if right_item.name() < left_item.name():
                        return RIGHT
                    else:  # if the names are the same order doesn't matter
                        return LEFT
            return EQUAL  # this shouldn't run but just in case

        def sort_children(item: TreeItem):
            item.children.sort(key=cmp_to_key(compare))

        # this is the actual code
        sort_children(self)
        for child in self.children:
            sort_children(child)

    def supports_subitems(self) -> bool:
        """Return whether the item supports subitems."""
        return self.linked_widget.supports_subitems()

    def supports_dragging(self) -> bool:
        """Returns whether the item can be dragged."""
        return self.linked_widget.supports_dragging()

    def process_type(
        self,
    ) -> type[Union["AbstractForegroundProcess", "AbstractBackgroundProcess"]] | None:
        """Returns the type of the linked process."""
        return self.linked_widget.process_type()

    def data(self) -> dict[str, Any]:
        """Get this item's widget data."""
        return self.linked_widget.to_dict()

    def expand_event(self):
        """Runs when the item is expanded in the view."""
        self.linked_widget.expand_event()

    def collapse_event(self):
        """Runs when the item is collapsed in the view."""
        self.linked_widget.collapse_event()

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def from_dict(
        cls: type[TreeItem], parent: TreeItem | None, item_as_dict: dict[str, Any]
    ) -> TreeItem:
        """
        Create a TreeItem from a JSON-style dictionary. This method is recursive.

        :param parent: The item's parent. This should be `None` if the item is the root item.
        :param item_as_dict: A dictionary representing the item's data in JSON format.
        """

        widget_type = ItemType.from_name(item_as_dict[Keys.TYPE]).value
        widget = widget_type.from_dict(item_as_dict[Keys.WIDGET_DATA])
        # cls is the type of the class (TreeItem in this case) and is passed implicitly
        item = cls(widget, parent)

        # add children
        for child_item_as_dict in item_as_dict[Keys.CHILDREN]:
            child_widget_type = ItemType.from_name(child_item_as_dict[Keys.TYPE]).value
            if child_widget_type.allowed_to_create():
                child_item = cls.from_dict(item, child_item_as_dict)
                item.append_children([child_item])

        return item

    def to_dict(self) -> dict[str, Any]:
        """Convert all of this item's data into a JSON-like dictionary."""
        item_as_dict: dict[str, Any] = dict()  # empty dictionary
        # convert the item ItemInfoType to a string

        item_as_dict[Keys.TYPE] = ItemType.from_widget(self.linked_widget).name
        # convert the widget data to a dictionary
        item_as_dict[Keys.WIDGET_DATA] = self.linked_widget.to_dict()
        # recursively create a list of dictionaries representing each child
        item_as_dict[Keys.CHILDREN] = [child.to_dict() for child in self.children]
        return item_as_dict
