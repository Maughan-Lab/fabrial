import json
import typing
from typing import Any, Iterable, Mapping, Self, Sequence

from PyQt6.QtCore import QDataStream, QMimeData, QModelIndex, QPersistentModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication

from ...utility.serde import Json
from ..tree_items import MutableTreeItem, SequenceItem, TreeItem
from .tree_model import JSON, TreeModel


class SequenceModel(TreeModel[SequenceItem]):
    """
    `TreeModel` for the sequence builder.

    Parameters
    ----------
    items
        The items in the model.
    """

    itemAdded = pyqtSignal(QModelIndex)
    """
    This is emitted every time an item is added to the model. Sends the `QModelIndex` of the item.
    """

    def __init__(self, items: Iterable[SequenceItem]):
        TreeModel.__init__(self, "Sequence", items)

    def init_from_jsonlike(self, items_as_json: Sequence[Mapping[str, Json]]) -> Self:
        """Initialize the model's data from a JSON-like structure."""
        # remove all items from the root
        self.removeRows(0, self.get_root().get_count(), QModelIndex())
        # deserialize the items
        items = [
            SequenceItem.from_dict(self.get_root(), item_as_json) for item_as_json in items_as_json
        ]
        self.insert_rows(0, QModelIndex(), items)
        return self

    def to_jsonlike(self) -> list[Json]:
        """Convert the model's data to a JSON-like structure."""
        return self.get_root().serialize()

    def data(self, index: QModelIndex, role: int | None = None) -> Any:  # implementation
        item = self.get_item(index)
        if item is not None:
            match role:
                case Qt.ItemDataRole.DisplayRole:
                    return item.get_display_name()
                case Qt.ItemDataRole.FontRole:
                    font = QApplication.font()
                    # items that are running are shown in bold
                    if item.is_active():
                        font.setBold(True)
                    return font
                case Qt.ItemDataRole.DecorationRole:
                    return item.get_icon()
        return None

    # ----------------------------------------------------------------------------------------------
    # overridden
    def removeRows(self, row: int, count: int, parent_index: QModelIndex = QModelIndex()) -> bool:
        if not self.is_enabled():
            return False

        parent_item: MutableTreeItem[SequenceItem] = self.get_item(parent_index) or self.get_root()
        self.beginRemoveRows(parent_index, row, row + count - 1)
        try:
            parent_item.remove_subitems(row, count)
            return True
        except IndexError:
            return False
        finally:
            self.endRemoveRows()

    # overridden
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

    # overridden
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

        if row != -1:  # the drop occurred above/below an item, insert appropriately
            begin_row = row
        elif parent_index.isValid():  # the drop occurred on an item, insert a child
            begin_row = 0
        else:  # the drop didn't occur on an item, so insert at the end
            begin_row = self.rowCount(parent_index)

        parent_item: TreeItem[SequenceItem] = self.get_item(parent_index) or self.get_root()

        items = []
        # NOTE: do not set the OpenModeFlag for this stream, it causes weird issues
        # cast is safe because we already check for `data` being `None` in `canDropMimeData()`
        stream = QDataStream(typing.cast(QMimeData, data).data(JSON))
        while not stream.atEnd():
            raw_text = stream.readQString()
            item_as_dict = json.loads(raw_text)
            item = SequenceItem.from_dict(parent_item, item_as_dict)
            items.append(item)

        self.insert_rows(begin_row, parent_index, items)

        return True

    def supportedDropActions(self) -> Qt.DropAction:  # overridden
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def supportedDragActions(self) -> Qt.DropAction:  # overridden
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    # ----------------------------------------------------------------------------------------------
    def insert_rows(self, row: int, parent_index: QModelIndex, items: Sequence[SequenceItem]):
        """Insert items into the model. Returns whether the operation succeeded."""
        if not self.is_enabled():
            return

        parent_item: MutableTreeItem[SequenceItem] = self.get_item(parent_index) or self.get_root()

        self.beginInsertRows(parent_index, row, row + len(items) - 1)
        parent_item.insert_subitems(row, items)
        self.endInsertRows()

        for i, item in enumerate(items):
            # notify that items were added
            self.itemAdded.emit(self.createIndex(row + i, 0, item))

    def paste_items(self, index: QModelIndex):
        """
        Paste items into the model from the clipboard.

        Parameters
        ----------
        index
            The index of the item to paste directly below.

        Returns
        -------
        Whether the operation succeeded.
        """
        clipboard = QApplication.clipboard()
        if clipboard is None:
            return

        data = clipboard.mimeData()
        if data is None:
            return

        success = self.dropMimeData(
            data,
            Qt.DropAction.CopyAction,
            index.row() + 1,  # drop below instead of above
            index.column(),
            index.parent(),
        )
        return success

    def delete_items(self, indexes: list[QModelIndex]) -> bool:
        """Delete items from the model. Returns whether the operation succeeded."""
        success = True
        # you need to use persistent indexes because you are modifying the model, so the indexes
        # must be updated
        persistent_indexes = [QPersistentModelIndex(index) for index in indexes]
        for index in persistent_indexes:
            if index.isValid():
                success = success and self.removeRow(index.row(), index.parent())
        return success
