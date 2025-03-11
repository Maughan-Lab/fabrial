from PyQt6.QtCore import (
    Qt,
    QModelIndex,
    QAbstractItemModel,
    QObject,
    QMimeData,
    QByteArray,
    QDataStream,
    QIODevice,
)
from tree_item import TreeItem
from typing import Iterable

JSON = "application/json"


class TreeModel(QAbstractItemModel):
    """Concrete ItemModel for representing trees."""

    def __init__(self, name: str, parent: QObject | None = None):
        super().__init__(parent)
        self.name = name
        self.root_item = TreeItem()
        self.items: list[TreeItem] = []

    def item(self, index: QModelIndex) -> TreeItem:
        """
        Get the item at the provided **index**. Returns the root item is **index** is invalid.
        """
        if index.isValid():
            # this uses C++ witchcraft to get the item at the index
            # look up the docs for QModelIndex
            # I think it is related to the index() function
            item: TreeItem = index.internalPointer()
            if item is not None:
                return item
        return self.root_item

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def parent(self, index: QModelIndex) -> QModelIndex:  # type: ignore
        item = self.item(index)
        if item is not None:
            parent_item = item.parent()
            if not parent_item:
                return QModelIndex()
        else:
            return QModelIndex()
        return self.createIndex(parent_item.child_index(), 0, parent_item)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 1

    def rowCount(self, parent_index: QModelIndex = QModelIndex()) -> int:
        parent_item = self.item(parent_index)
        return parent_item.child_count()

    def data(self, index: QModelIndex, role: int | None = None) -> str | None:
        if not index.isValid():
            return None
        match role:
            case Qt.ItemDataRole.DisplayRole:
                item = self.item(index)
                return item.name()  # type: ignore
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = super().flags(index)  # default implementation
        if index.isValid():
            return flags | Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsDropEnabled
        return flags | Qt.ItemFlag.ItemIsDropEnabled

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int | None = None
    ) -> str | None:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.name
        return None

    def index(
        self, row: int, column: int, parent_index: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        parent_item = self.item(parent_index)
        if parent_item is None:
            return QModelIndex()
        child_item = parent_item.child(row)
        if child_item is not None:
            # createIndex() is defined by QAbstractItemModel
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def insertRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        parent_item = self.item(parent_index)
        if parent_item is None:
            return False
        # beginInsertRows() is defined by QAbstractItemModel and it notifies other components rows
        # are being added
        self.beginInsertRows(parent_index, row, row + count - 1)  # type: ignore
        success = parent_item.insert_children(row, count)
        self.endInsertRows()
        return success

        # NOTE: the function that triggers this method MUST call link_widget() on the newly created
        # TreeItem to associate the data.

    def removeRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        if not parent_index.isValid():  # type: ignore
            return False
        parent_item = self.item(parent_index)

        self.beginRemoveRows(parent_index, row, row + count - 1)  # type: ignore
        success = parent_item.remove_children(row, count)
        self.endRemoveRows()
        return success

    def supportedDropActions(self) -> Qt.DropAction:
        return Qt.DropAction.MoveAction | Qt.DropAction.CopyAction

    def mimeTypes(self):
        return [JSON]

    def mimeData(self, indexes: Iterable[QModelIndex]):
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.WriteOnly)
        for index in indexes:
            if index.isValid():
                text = self.data(index, Qt.ItemDataRole.DisplayRole)
                stream.writeQString(text)

        mime_data.setData(JSON, encoded_data)
        return mime_data

    def canDropMimeData(
        self,
        data: QMimeData | None,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent_index: QModelIndex,
    ):
        if data is None or not data.hasFormat(JSON):
            return False
        match action:
            case Qt.DropAction.CopyAction | Qt.DropAction.MoveAction:
                return True
        return False

    def dropMimeData(
        self,
        data: QMimeData | None,
        action: Qt.DropAction,
        row: int,
        column: int,
        parent_index: QModelIndex,
    ) -> bool:
        if not self.canDropMimeData(data, action, row, column, parent_index):
            return False

        begin_row: int
        if row != -1:  # the drop occurred above/below an item, insert appropriately
            begin_row = row
        elif parent_index.isValid():  # the drop occurred on an item, insert a child
            begin_row = 0
        else:  # the drop didn't occur on an item, so insert at the end
            begin_row = self.rowCount(parent_index)

        # NOTE: do not set the OpenModeFlag for this stream, it causes weird issues
        stream = QDataStream(data.data(JSON))  # type: ignore
        item_data: list[str] = []
        while not stream.atEnd():
            text = stream.readQString()
            item_data.append(text)

        self.insertRows(begin_row, len(item_data), parent_index)
        for text in item_data:
            index = self.index(begin_row, 0, parent_index)
            item = self.item(index)
            item.display_name = text
            begin_row += 1
        return True

    # TODO: implement drag and drop and deleting with the Delete key or a button
