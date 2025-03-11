from PyQt6.QtCore import Qt, QModelIndex, QAbstractItemModel, QObject
from PyQt6.QtGui import QKeyEvent, QDropEvent
from PyQt6.QtWidgets import QFileDialog, QTreeView, QWidget, QAbstractItemView
from tree_item import TreeItem


class SequenceTreeView(QTreeView):
    """Custom QTreeView for displaying sequence settings."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.doubleClicked.connect(self.handle_double_click)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def handle_double_click(self, index: QModelIndex):
        """On a double click event."""
        # TODO: this needs to grab the TreeItem and show its widget in a new (secondary) window
        item: TreeItem = index.internalPointer()
        print(index.internalPointer())

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
                    # TODO: show the item's linked widget
                    # this will involve either creating a new window and putting the widget there,
                    # or using the widget as the window itself. I'm not sure if closing the widget
                    # deletes it
                    print("Enter pressed, this should show the widget.")

        super().keyPressEvent(event)

    def dropEvent(self, event: QDropEvent | None):
        if event is not None:
            # event.setDropAction(Qt.DropAction.MoveAction)
            super().dropEvent(event)
            self.model().layoutChanged.emit()  # type: ignore
