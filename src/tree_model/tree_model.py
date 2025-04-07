from PyQt6.QtCore import (
    Qt,
    QModelIndex,
    QPersistentModelIndex,
    QAbstractItemModel,
    QObject,
    QMimeData,
    QByteArray,
    QDataStream,
    QIODevice,
    pyqtSignal,
)
from .tree_item import TreeItem
from .clipboard import CLIPBOARD
from typing import Iterable, Self
import json

JSON = "application/json"


class TreeModel(QAbstractItemModel):
    """Concrete ItemModel for representing trees."""

    dropOccurred = pyqtSignal(QModelIndex)

    def __init__(self, name: str = "", parent: QObject | None = None):
        """
        :param name: The name displayed at the top of the widget.
        :param parent: (optional) The owner of this widget.
        """
        super().__init__(parent)
        self.name = name
        self.root_item = TreeItem()

        # don't access these directly
        self.supported_drop_actions = Qt.DropAction.CopyAction
        self.supported_drag_actions = self.supported_drop_actions

    def initialize_from_file(self, filename: str) -> Self:
        """Initialize the model's data from a file."""
        data = json.load(open(filename, "r"))
        self.root_item = TreeItem.from_dict(None, data)
        return self

    @classmethod
    def from_file(cls: type[Self], name: str, filename: str) -> Self:
        """
        Create a model from a .json file.

        :param name: The name displayed at the top of the widget.
        :param filename: The name of the initialization file. Must be a .json file with the proper
        format.
        """
        model = cls(name).initialize_from_file(filename)
        return model

    def alphabetize_all(self) -> Self:
        """Alphabetize all of this model's items by display name."""
        self.root_item.recursively_sort_children()
        return self

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

    def insert_rows(self, row: int, parent_index: QModelIndex, items: list[TreeItem]) -> bool:
        """Insert items into the model. Returns True on success, False on failure."""
        parent_item = self.item(parent_index)
        self.beginInsertRows(parent_index, row, row + len(items) - 1)
        success = parent_item.insert_children(row, items)
        self.endInsertRows()

        return success

    def set_supported_drag_actions(self, actions: Qt.DropAction):
        """Change the supported drag options (default CopyAction)."""
        self.supported_drag_actions = actions

    def set_supported_drop_actions(self, actions: Qt.DropAction):
        """Change the supported drop options (default CopyAction)."""
        self.supported_drop_actions = actions

    def copy_items(self, indexes: Iterable[QModelIndex]) -> bool:
        """
        Copy items to the clipboard. Returns whether the operation succeeded (currently we assume it
        always succeeds).
        """
        data = self.mimeData(sorted(indexes))
        CLIPBOARD.set_contents(data)
        return True

    def paste_items(self, index: QModelIndex) -> bool:
        """
        Paste items into the model from the clipboard.

        :param index: The index of the item to paste directly below.
        :returns: Whether the operation succeeded.
        """
        data = CLIPBOARD.contents()
        if data is not None:
            success = self.dropMimeData(
                data,
                Qt.DropAction.CopyAction,
                index.row() + 1,  # drop below instead of above
                index.column(),
                index.parent(),
            )
        else:
            return False
        return success

    def delete_items(self, indexes: Iterable[QModelIndex]) -> bool:
        """Delete items from the model. Returns whether the operation succeeded."""
        success = True
        # you need to use persistent indexes because you are modifying the model, so the indexes
        # must be updated
        persistent_indexes = [QPersistentModelIndex(index) for index in indexes]
        for index in persistent_indexes:
            if index.isValid():
                success = self.removeRow(index.row(), index.parent())
        return success

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

    def removeRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        parent_item = self.item(parent_index)

        self.beginRemoveRows(parent_index, row, row + count - 1)  # type: ignore
        success = parent_item.remove_children(row, count)
        self.endRemoveRows()
        return success

    def supportedDropActions(self) -> Qt.DropAction:
        return self.supported_drop_actions

    def supportedDragActions(self) -> Qt.DropAction:
        return self.supported_drag_actions

    def mimeTypes(self) -> list[str]:
        return [JSON]

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:
        mime_data = QMimeData()
        encoded_data = QByteArray()
        stream = QDataStream(encoded_data, QIODevice.OpenModeFlag.WriteOnly)
        for index in indexes:
            if index.isValid():
                item = self.item(index)
                text = json.dumps(item.to_dict())
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
    ) -> bool:
        parent_item = self.item(parent_index)
        if (
            not parent_item.supports_subitems()
            or data is None
            or not data.hasFormat(JSON)
            or not action & self.supportedDropActions()
        ):
            return False
        return True

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
        items: list[TreeItem] = []
        parent_item = self.item(parent_index)
        while not stream.atEnd():
            raw_text = stream.readQString()
            item_as_dict = json.loads(raw_text)
            item = TreeItem.from_dict(parent_item, item_as_dict)
            items.append(item)

        self.insert_rows(begin_row, parent_index, items)

        for i, item in enumerate(items):
            self.dropOccurred.emit(self.createIndex(begin_row + i, 0, item))

        self.layoutChanged.emit()

        return True
