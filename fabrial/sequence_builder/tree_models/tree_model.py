import json
from abc import abstractmethod
from collections.abc import Iterable
from typing import Any

from PyQt6.QtCore import (
    QAbstractItemModel,
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
    QModelIndex,
    Qt,
)
from PyQt6.QtWidgets import QApplication

from ...classes import QABC
from ..tree_items import RootItem, TreeItem

JSON = "application/json"


class TreeModel[Item: TreeItem](QAbstractItemModel, QABC):
    """
    `QAbstractItemModel` for representing trees.

    Parameters
    ----------
    name
        The name displayed at the top of the widget.
    items
        The items to initialize with. Can be empty.
    """

    def __init__(self, title: str, items: Iterable[Item]):
        QAbstractItemModel.__init__(self)

        self.name = title
        self.root_item: RootItem[Item] = RootItem()
        self.root_item.append_subitems(items)

        self.base_flag = Qt.ItemFlag.ItemIsEnabled

    def title(self) -> str:
        """Get the model's title."""
        return self.name

    def root(self) -> RootItem[Item]:
        """Get the root item."""
        return self.root_item

    def copy_items(self, indexes: Iterable[QModelIndex]):
        """Copy items to the clipboard."""
        data = self.mimeData(sorted(indexes))
        clipboard = QApplication.clipboard()
        if clipboard is not None:
            clipboard.setMimeData(data)

    def is_enabled(self) -> bool:
        "Whether the model's items are enabled."
        return self.base_flag != Qt.ItemFlag.NoItemFlags

    def set_enabled(self, enabled: bool):
        """Set whether the model's items are enabled."""
        self.base_flag = Qt.ItemFlag.ItemIsEnabled if enabled else Qt.ItemFlag.NoItemFlags

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # overridden
        flags = self.base_flag
        item = self.get_item(index)
        if item is None:
            # probably unnecessary, but just in case
            if self.root_item.supports_subitems():
                flags |= Qt.ItemFlag.ItemIsDropEnabled
            return flags

        if item.supports_subitems():
            flags |= Qt.ItemFlag.ItemIsDropEnabled
        if item.supports_dragging():
            flags |= Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsSelectable
        return flags

    @abstractmethod
    def data(self, index: QModelIndex, role: int | None = None) -> Any:  # overridden
        ...

    def get_item(self, index: QModelIndex) -> Item | None:
        """Get the item at the provided **index**. Returns `None` if **index** is invalid."""
        if index.isValid():
            # this uses C++ witchcraft to get the item at the index
            # look up the docs for QModelIndex
            # I think it is related to the index() function
            # it's something with pointers, idk
            item: Item | None = index.internalPointer()
            if item is not None:
                return item
        return None

    # ----------------------------------------------------------------------------------------------
    # overridden
    def parent(self, index: QModelIndex) -> QModelIndex:  # type: ignore
        item = self.get_item(index)
        if item is None:
            return QModelIndex()

        parent_item = item.parent()
        if parent_item is None:
            return QModelIndex()

        row = parent_item.index_in_parent()
        if row is None:
            return QModelIndex()

        return self.createIndex(row, 0, parent_item)

    def columnCount(self, parent: QModelIndex | None = None) -> int:  # overridden
        return 1

    def rowCount(self, index: QModelIndex = QModelIndex()) -> int:  # overridden
        item: TreeItem = self.get_item(index) or self.root_item
        return item.subitem_count()

    # overridden
    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int | None = None
    ) -> str | None:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.title()
        return None

    # overridden
    def index(
        self, row: int, column: int, parent_index: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        parent_item: TreeItem = self.get_item(parent_index) or self.root_item
        item = parent_item.get_subitem(row)
        if item is None:
            return QModelIndex()
        return self.createIndex(row, column, item)

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData | None:  # overridden
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.WriteOnly)
        for index in indexes:
            item = self.get_item(index)
            if item is not None:
                text = json.dumps(item.serialize())
                stream.writeQString(text)

        if encoded_data.length() == 0:
            return None  # return `None` instead of an empty `QMimeData`

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
