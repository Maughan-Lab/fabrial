from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QKeyEvent, QDropEvent
from PyQt6.QtWidgets import QTreeView, QWidget
from .tree_item import TreeItem
from .tree_model import TreeModel


class SequenceTreeView(QTreeView):
    """Custom QTreeView for displaying sequence settings."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.doubleClicked.connect(self.handle_double_click)
        self.setExpandsOnDoubleClick(False)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def handle_double_click(self, index: QModelIndex):
        """On a double click event."""
        model: TreeModel = self.model()  # type: ignore
        model.item(index).show_widget()

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def keyPressEvent(self, event: QKeyEvent | None):
        if event is not None:
            model = self.model()
            selection_model = self.selectionModel()
            index = selection_model.currentIndex()  # type: ignore
            match event.key():
                case Qt.Key.Key_Delete:  # delete the current item
                    model.removeRow(index.row(), index.parent())  # type: ignore
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    item: TreeItem = index.internalPointer()
                    item.show_widget()
        super().keyPressEvent(event)

    def dropEvent(self, event: QDropEvent | None):
        if event is not None:
            # event.setDropAction(Qt.DropAction.MoveAction)
            super().dropEvent(event)
            self.model().layoutChanged.emit()  # type: ignore
            # expand one level so the dropped data is more visible
            index = self.indexAt(event.position().toPoint())
            self.expandRecursively(index, 1)
            # TODO: change the dropAction depending on if Ctrl is held (if it is, do a copy, not a move)
