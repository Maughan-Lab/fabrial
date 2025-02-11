from PyQt6.QtWidgets import QWidget


class TreeItem:
    """Class to represent items on a tree model."""

    def __init__(self, parent: "TreeItem" | None = None):
        self.linked_widget: QWidget
        self.parent_item = parent
        self.children: list["TreeItem"] = []

    def link_widget(self, widget: QWidget):
        """Link **widget** to this item (for data storage)."""

    def child(self, index: int) -> "TreeItem" | None:
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
        return ""

    def insert_children(self, starting_row_index: int, count: int) -> bool:
        """
        Insert **count** children starting at **starting_row_index**, with the newest children on
        top. Returns True if successful, False otherwise.
        """
        try:
            for _ in range(count):
                item = TreeItem(self)
                self.children.insert(starting_row_index, item)
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
