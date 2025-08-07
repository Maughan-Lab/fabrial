import json
from abc import abstractmethod
from typing import Any, Iterable, Protocol

from PyQt6.QtCore import (
    QAbstractItemModel,
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
    QModelIndex,
    Qt,
)

from ..clipboard import Clipboard
from ..tree_items import RootItem, SequenceItem, TreeItem

JSON = "application/json"


class TreeModel[ItemType: TreeItem[SequenceItem]](QAbstractItemModel, Protocol):
    """
    `QAbstractItemModel` for representing trees.

    Parameters
    ----------
    name
        The name displayed at the top of the widget.
    items
        The items to initialize with. Can be empty.
    clipboard
        The `Clipboard` to copy items to.
    """

    @abstractmethod
    def get_title(self) -> str:
        """Get the model's title."""
        ...

    @abstractmethod
    def get_root(self) -> RootItem[ItemType]:
        """Get the root item."""
        ...

    @abstractmethod
    def copy_items(self, indexes: Iterable[QModelIndex]):
        """Copy items to the clipboard."""
        ...

    @abstractmethod
    def is_enabled(self) -> bool:
        "Whether the model's items are enabled."
        ...

    @abstractmethod
    def set_enabled(self, enabled: bool):
        """Set whether the model's items are enabled."""
        ...

    @abstractmethod
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # overridden
        ...

    @abstractmethod
    def data(self, index: QModelIndex, role: int | None = None) -> Any:  # overridden
        ...

    def get_item(self, index: QModelIndex) -> ItemType | None:
        """
        Get the item at the provided **index**. Returns `None` if **index** is invalid.
        """
        if index.isValid():
            # this uses C++ witchcraft to get the item at the index
            # look up the docs for QModelIndex
            # I think it is related to the index() function
            # it's something with pointers, idk
            item: ItemType | None = index.internalPointer()
            if item is not None:
                return item
        return None

    # ----------------------------------------------------------------------------------------------
    # overridden
    def parent(self, index: QModelIndex) -> QModelIndex:  # type: ignore
        # TODO: make sure this is all correct
        item = self.get_item(index)
        if item is None:
            return QModelIndex()

        parent_item = item.get_parent()
        if parent_item is None:
            return QModelIndex()

        row = parent_item.index_in_parent()
        if row is None:
            return QModelIndex()

        return self.createIndex(row, 0, parent_item)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # overridden
        return 1

    def rowCount(self, parent_index: QModelIndex = QModelIndex()) -> int:  # overridden
        parent_item = self.get_item(parent_index)
        if parent_item is not None:
            return parent_item.get_count()
        else:
            return self.get_root().get_count()

    # overridden
    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int | None = None
    ) -> str | None:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.get_title()
        return None

    # overridden
    def index(
        self, row: int, column: int, parent_index: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        parent_item = self.get_item(parent_index)
        if parent_item is None:
            return QModelIndex()
        child_item = parent_item.get_subitem(row)
        if child_item is not None:
            # createIndex() is defined by QAbstractItemModel
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:  # overridden
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.WriteOnly)
        for index in indexes:
            item = self.get_item(index)
            if item is not None:
                text = json.dumps(item.serialize())
                stream.writeQString(text)

        mime_data.setData(JSON, encoded_data)
        return mime_data

    def mimeTypes(self) -> list[str]:  # overridden
        return [JSON]

    def expand_event(self, index: QModelIndex):
        """Handle an item being expanded in the view."""
        item = self.get_item(index)
        if item is not None:
            item.expand_event()

    def collapse_event(self, index: QModelIndex):
        """Handle an item being collapsed in the view."""
        item = self.get_item(index)
        if item is not None:
            item.collapse_event()


def copy_items[SubItem: TreeItem[SequenceItem]](
    model: TreeModel[SubItem], clipboard: Clipboard, indexes: Iterable[QModelIndex]
):
    """
    Helper function for `TreeModel.copy_items()`. Gets the items at **indexes** in **model** and
    copies them to the **clipboard**.
    """
    data = model.mimeData(sorted(indexes))
    clipboard.set_contents(data)


def flags[SubItem: TreeItem[SequenceItem]](
    model: TreeModel[SubItem], base_flag: Qt.ItemFlag, index: QModelIndex
) -> Qt.ItemFlag:
    """Helper function for `TreeModel.flags()`."""
    item = model.get_item(index)
    if item is None:
        return base_flag

    flags = base_flag
    if item.supports_subitems():
        flags |= Qt.ItemFlag.ItemIsDropEnabled
    if item.supports_dragging():
        flags |= Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsSelectable
    return flags
