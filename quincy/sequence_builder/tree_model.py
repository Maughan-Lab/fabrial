import json
from os import PathLike
from typing import Any, Iterable, Self

from PyQt6.QtCore import (
    QAbstractItemModel,
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    pyqtSignal,
)
from PyQt6.QtWidgets import QApplication

from ..utility import sequence_builder
from .clipboard import CLIPBOARD
from .tree_item import TreeItem

JSON = "application/json"


class TreeModel(QAbstractItemModel):
    """Concrete ItemModel for representing trees."""

    itemAdded = pyqtSignal(QModelIndex)
    """
    This is emitted every time an item is added to the model. Sends the **QModelIndex** of the item.
    """

    def __init__(self, name: str = "", parent: QObject | None = None):
        """
        :param name: The name displayed at the top of the widget.
        :param parent: (optional) The owner of this widget.
        """
        QAbstractItemModel.__init__(self, parent)
        self.name = name
        self.root_item = TreeItem.create_root_item()

        # don't access these directly
        self.supported_drop_actions = Qt.DropAction.CopyAction
        self.supported_drag_actions = self.supported_drop_actions
        self.base_flag = Qt.ItemFlag.ItemIsEnabled

    def init_from_dict(self, root_item_as_dict: dict[str, Any]) -> Self:
        """Initialize the model's data from a dictionary."""
        self.root_item = TreeItem.from_dict(None, root_item_as_dict)
        self.layoutChanged.emit()
        return self

    def init_from_directory(self, directory_path: PathLike | str) -> Self:
        """Initialize the model's data from a properly formatted directory and sort the items."""
        return self.init_from_dict(
            sequence_builder.item_dict_from_directory(directory_path)
        ).sort_all()

    def to_dict(self) -> dict[str, Any]:
        """Convert this model's item data to a JSON-like dictionary."""
        return self.root_item.to_dict()

    def sort_all(self) -> Self:
        """
        Sort all of this model's items by display name. Items containing other items are listed
        first.
        """
        self.root_item.sort_all()
        return self

    def item(self, index: QModelIndex) -> TreeItem:
        """
        Get the item at the provided **index**. Returns the root item is **index** is invalid.
        """
        if index.isValid():
            # this uses C++ witchcraft to get the item at the index
            # look up the docs for QModelIndex
            # I think it is related to the index() function
            # it's something with pointers, idk
            item: TreeItem = index.internalPointer()
            if item is not None:
                return item
        return self.root_item

    def root(self) -> TreeItem:
        """Get the root item."""
        return self.root_item

    def insert_rows(self, row: int, parent_index: QModelIndex, items: list[TreeItem]) -> bool:
        """Insert items into the model. Returns True on success, False on failure."""
        if self.is_enabled():
            parent_item = self.item(parent_index)
            self.beginInsertRows(parent_index, row, row + len(items) - 1)
            success = parent_item.insert_children(row, items)
            self.endInsertRows()

            for i, item in enumerate(items):
                # notify that items were added
                self.itemAdded.emit(self.createIndex(row + i, 0, item))

            return success
        return False

    def set_supported_drag_actions(self, actions: Qt.DropAction):
        """Change the supported drag options (default CopyAction)."""
        self.supported_drag_actions = actions

    def set_supported_drop_actions(self, actions: Qt.DropAction):
        """Change the supported drop options (default CopyAction)."""
        self.supported_drop_actions = actions

    def copy_items(self, indexes: list[QModelIndex]) -> bool:
        """
        Copy items to the clipboard. Returns whether the operation succeeded (currently we assume it
        always succeeds).
        """
        if len(indexes) > 0:
            data = self.mimeData(sorted(indexes))
            CLIPBOARD.set_contents(data)
            return True
        return False

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

    def delete_items(self, indexes: list[QModelIndex]) -> bool:
        """Delete items from the model. Returns whether the operation succeeded."""
        success = True
        # you need to use persistent indexes because you are modifying the model, so the indexes
        # must be updated
        persistent_indexes = [QPersistentModelIndex(index) for index in indexes]
        for index in persistent_indexes:
            if index.isValid():
                success = self.removeRow(index.row(), index.parent())
        return success

    def is_enabled(self) -> bool:
        "Whether the model's items are enabled."
        return self.base_flag != Qt.ItemFlag.NoItemFlags

    def set_enabled(self, enabled: bool):
        """Set whether the model's items are enabled."""
        self.base_flag = Qt.ItemFlag.ItemIsEnabled if enabled else Qt.ItemFlag.NoItemFlags

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

    def data(self, index: QModelIndex, role: int | None = None) -> Any:
        if not index.isValid():
            return None
        item = self.item(index)
        match role:
            case Qt.ItemDataRole.DisplayRole:
                return item.name()
            case Qt.ItemDataRole.FontRole:
                # items that are running are shown in bold
                if item.is_running():
                    font = QApplication.font()
                    font.setBold(True)
                    return font
            case Qt.ItemDataRole.DecorationRole:
                return item.widget().icon()
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = self.base_flag
        item = self.item(index)
        if item.supports_subitems():
            flags |= Qt.ItemFlag.ItemIsDropEnabled
        if item.supports_dragging():
            flags |= Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsSelectable
        return flags

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
        if self.is_enabled():
            parent_item = self.item(parent_index)

            self.beginRemoveRows(parent_index, row, row + count - 1)  # type: ignore
            success = parent_item.remove_children(row, count)
            self.endRemoveRows()
            return success
        return False

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
        if data is None or not data.hasFormat(JSON) or not action & self.supportedDropActions():
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

        self.layoutChanged.emit()

        return True

    def expand_event(self, index: QModelIndex):
        """Handle an item being expanded in the view."""
        self.item(index).expand_event()

    def collapse_event(self, index: QModelIndex):
        """Handle an item being collapsed in the view."""
        self.item(index).collapse_event()
