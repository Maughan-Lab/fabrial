from typing import Union, Any
from .items.base.widget import BaseWidget
from .items.root.widget import NullWidget
from .items.base.item_info import BaseItemInfo
from .items.root.item_info import RootItemInfo
from .items.base.process import BaseProcess
from .items.type_info import TypeInfo


TYPE = "linked-widget-type"
WIDGET_DATA = "linked-widget-data"
CHILDREN = "children"


class TreeItem:
    """
    Class to represent items on a tree model. You must override:
    - `widget_type()` as a static method
    - `process_type()` as a static method
    """

    def __init__(
        self,
        item_info: type[BaseItemInfo] = RootItemInfo,
        parent: Union["TreeItem", None] = None,
        linked_widget: BaseWidget | NullWidget = NullWidget(),
    ):
        self.item_info = item_info

        self.parent_item = parent
        self.linked_widget = linked_widget
        self.children: list["TreeItem"] = []
        self.supports_children = item_info.SUPPORTS_SUBITEMS

    def show_widget(self):
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
        return self.linked_widget.display_name()

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

    def set_supports_subitems(self, supports_subitems: bool):
        """Set whether the item supports subitems (i.e. children)."""
        self.supports_children = supports_subitems

    def supports_subitems(self) -> bool:
        """Return whether the item supports subitems. By default, subitems are not supported."""
        return self.supports_children

    def process_type(self) -> type[BaseProcess]:
        """Returns the type of the linked process."""
        return self.item_info.PROCESS_TYPE

    # ----------------------------------------------------------------------------------------------
    @classmethod
    def from_dict(
        cls: type["TreeItem"], parent: Union["TreeItem", None], item_as_dict: dict[str, Any]
    ) -> "TreeItem":
        """
        Create a TreeItem from a JSON-style dictionary. This method is recursive.

        :param parent: The item's parent. This should be `None` if the item is the root item.
        :param item_as_dict: A dictionary representing the item's data in JSON format.
        """

        item_info = TypeInfo.from_name(item_as_dict[TYPE]).value
        widget = item_info.WIDGET_TYPE.from_dict(item_as_dict[WIDGET_DATA])
        # cls is the type of the class (TreeItem in this case) and is passed implicitly
        item = cls(item_info, parent, widget)

        # add children
        for child_item_as_dict in item_as_dict[CHILDREN]:
            child_item = cls.from_dict(item, child_item_as_dict)
            item.append_children([child_item])

        return item

    def to_dict(self) -> dict[str, Any]:
        """Convert all of this item's data into a JSON-like dictionary."""
        item_as_dict: dict[str, Any] = dict()  # empty dictionary
        # convert the item TypeInfo to a string
        item_as_dict[TYPE] = TypeInfo.from_item_info(self.item_info).name
        # convert the widget data to a dictionary
        item_as_dict[WIDGET_DATA] = self.linked_widget.to_dict()
        # recursively create a list of dictionaries representing each child
        item_as_dict[CHILDREN] = [child.to_dict() for child in self.children]
        return item_as_dict
