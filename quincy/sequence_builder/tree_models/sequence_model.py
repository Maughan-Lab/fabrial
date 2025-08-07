import json
from os import PathLike
from typing import Any, Iterable, Mapping, Self, Sequence

from PyQt6.QtCore import QDataStream, QMimeData, QModelIndex, QPersistentModelIndex, Qt, pyqtSignal
from PyQt6.QtWidgets import QApplication

from ...utility.serde import Json
from ..clipboard import Clipboard
from ..tree_items import RootItem, SequenceItem
from . import tree_model
from .tree_model import JSON, TreeModel


class SequenceModel(TreeModel[SequenceItem]):
    """`TreeModel` for the sequence builder."""

    itemAdded = pyqtSignal(QModelIndex)
    """
    This is emitted every time an item is added to the model. Sends the `QModelIndex` of the item.
    """

    def __init__(self, items: Iterable[SequenceItem], clipboard: Clipboard):
        self.root_item: RootItem[SequenceItem] = RootItem()
        self.root_item.append_subitems(items)
        self.clipboard = clipboard

        self.base_flag = Qt.ItemFlag.ItemIsEnabled

    def init_from_file(self, file: PathLike[str] | str) -> Self:
        """Initialize the model's data from a JSON file."""
        # remove all items from the root
        self.root_item.remove_subitems(0, self.root_item.get_count())
        # load the file (this assumes it contains a sequence of `SequenceItem` representations)
        with open(file, "r") as f:
            items_as_dicts: Sequence[Mapping[str, Json]] = json.load(f)
        # deserialize the dictionaries
        items = [
            SequenceItem.from_dict(self.root_item, item_as_dict) for item_as_dict in items_as_dicts
        ]
        self.root_item.append_subitems(items)  # add the new items
        return self

    def to_file(self, file: PathLike[str] | str) -> bool:
        """
        Save this model's data to a JSON file. Returns whether the operation succeeded.
        """
        try:
            serialized_root = self.get_root().serialize()
            with open(file, "w") as f:
                json.dump(serialized_root, f)
            return True
        except Exception:
            return False

    def get_title(self) -> str:  # implementation
        return "Sequence"

    def get_root(self) -> RootItem[SequenceItem]:  # implementation
        return self.root_item

    def copy_items(self, indexes: Iterable[QModelIndex]):  # implementation
        tree_model.copy_items(self, self.clipboard, indexes)

    def is_enabled(self):  # implementation
        return self.base_flag != Qt.ItemFlag.NoItemFlags

    def set_enabled(self, enabled: bool):  # implementation
        self.base_flag = Qt.ItemFlag.ItemIsEnabled if enabled else Qt.ItemFlag.NoItemFlags

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:  # implementation
        return tree_model.flags(self, self.base_flag, index)

    def data(self, index: QModelIndex, role: int | None = None) -> Any:  # implementation
        item = self.get_item(index)
        if item is None:
            return None

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

        parent_item = self.get_item(parent_index)
        if parent_item is None:
            return False

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
        # I know we already check in `canDropMimeData()`, but for typing we have to check again
        if data is None:
            return False

        if row != -1:  # the drop occurred above/below an item, insert appropriately
            begin_row = row
        elif parent_index.isValid():  # the drop occurred on an item, insert a child
            begin_row = 0
        else:  # the drop didn't occur on an item, so insert at the end
            begin_row = self.rowCount(parent_index)

        parent_item = self.get_item(parent_index)
        if parent_item is None:
            return False

        items = []
        # NOTE: do not set the OpenModeFlag for this stream, it causes weird issues
        stream = QDataStream(data.data(JSON))
        while not stream.atEnd():
            raw_text = stream.readQString()
            item_as_dict = json.loads(raw_text)
            item = SequenceItem.from_dict(parent_item, item_as_dict)
            items.append(item)

        self.insert_rows(begin_row, parent_index, items)

        self.layoutChanged.emit()

        return True

    def supportedDropActions(self) -> Qt.DropAction:  # overridden
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    def supportedDragActions(self) -> Qt.DropAction:  # overridden
        return Qt.DropAction.CopyAction | Qt.DropAction.MoveAction

    # ----------------------------------------------------------------------------------------------
    def insert_rows(self, row: int, parent_index: QModelIndex, items: Sequence[SequenceItem]):
        """Insert items into the model. Returns whether the operation succeeded."""
        if not self.is_enabled():
            return False

        parent_item = self.get_item(parent_index)
        if parent_item is None:
            return False

        self.beginInsertRows(parent_index, row, row + len(items) - 1)
        parent_item.insert_subitems(row, items)
        self.endInsertRows()

        for i, item in enumerate(items):
            # notify that items were added
            self.itemAdded.emit(self.createIndex(row + i, 0, item))

    def paste_items(self, index: QModelIndex) -> bool:
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
        data = self.clipboard.contents()
        if data is None:
            return False

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
                success = self.removeRow(index.row(), index.parent())
        return success
