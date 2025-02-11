from PyQt6.QtCore import Qt, QModelIndex, QAbstractItemModel, QObject
from .tree_item import TreeItem


class TreeModel(QAbstractItemModel):
    """Concrete ItemModel for representing trees."""

    def __init__(self, name: str, parent: QObject | None = None):
        super().__init__(parent)
        self.name = name
        self.items: list[TreeItem] = []

    def item(self, index: QModelIndex | None) -> TreeItem | None:
        """Get the item at the provided **index**. Returns **None** if **index** is **None**."""
        if index is not None:
            # this uses C++ witchcraft to get the item at the index
            # look up the docs for QModelIndex
            # I think it is related to the index() function
            item: TreeItem = index.internalPointer()
            if item is not None:
                return item
        return None

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def parent(self, index: QModelIndex) -> QModelIndex:  # type: ignore
        item = self.item(index)
        if item is not None:
            parent_item = item.parent()
        else:
            return QModelIndex()
        return self.createIndex(parent_item.child_index(), 0, parent_item)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 1

    def rowCount(self, parent_index: QModelIndex | None = None) -> int:
        # TODO: implement
        pass

    def data(self, index: QModelIndex, role: int | None = None):
        match role:
            case Qt.ItemDataRole.DisplayRole | Qt.ItemDataRole.EditRole:
                item = self.item(index)
                return item.name()  # type: ignore

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return super().flags(index)  # default implementation

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int | None = None
    ) -> str | None:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.name
        return None

    def index(self, row: int, column: int, parent_index: QModelIndex | None = None) -> QModelIndex:
        parent_item = self.item(parent_index)
        if parent_item is None:
            return QModelIndex()
        child_item = parent_item.child(row)
        if child_item is not None:
            # createIndex() is defined by QAbstractItemModel
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def insertRows(self, row: int, count: int, index: QModelIndex | None = None) -> bool:
        parent_item = self.item(index)
        if parent_item is None:
            return False
        # beginInsertRows() is defined by QAbstractItemModel and it notifies other components a row
        # is being added
        self.beginInsertRows(index, row, row + count - 1)  # type: ignore
        success = parent_item.insert_children(row, count)
        self.endInsertRows()
        return success

        # NOTE: the function that triggers this method MUST call link_widget() on the newly created
        # TreeItem to associate the data.

    def removeRows(self, row: int, count: int, parent_index: QModelIndex | None = None) -> bool:
        parent_item = self.item(parent_index)
        if parent_item is None:
            return False

        self.beginRemoveRows(parent_index, row, row + count - 1)  # type: ignore
        success = parent_item.remove_children(row, count)
        self.endRemoveRows()
        return success

    # TODO: implement RowCount() (above), maybe setData() (to open the widget to edit data)
    # TODO: implement drag and drop and deleting with the Delete key or a button

    # ----------------------------------------------------------------------------------------------
