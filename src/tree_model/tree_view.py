from PyQt6.QtCore import Qt, QModelIndex, QItemSelectionModel
from PyQt6.QtGui import QKeyEvent, QDropEvent
from PyQt6.QtWidgets import QTreeView, QWidget, QAbstractItemView
from .tree_item import TreeItem
from .tree_model import TreeModel


class SequenceTreeView(QTreeView):
    """Custom QTreeView for displaying sequence settings."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setExpandsOnDoubleClick(False)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.doubleClicked.connect(self.handle_double_click)

        model = TreeModel("Sequence")
        model.set_supported_drag_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        model.set_supported_drop_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        self.setModel(model)

        model.dropOccurred.connect(lambda index: self.expand(index))

    def connect_signals(self):
        model: TreeModel = self.model()  # type: ignore
        # expand one level so the dropped data is more visible
        model.dropOccurred.connect(lambda index: self.expand(index))

    def handle_double_click(self, index: QModelIndex):
        """On a double click event."""
        model: TreeModel = self.model()  # type: ignore
        model.item(index).show_widget()

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def keyPressEvent(self, event: QKeyEvent | None):
        if event is not None:
            model: TreeModel = self.model()  # type: ignore
            selection_model: QItemSelectionModel = self.selectionModel()  # type: ignore
            index = selection_model.currentIndex()
            match event.key():
                case Qt.Key.Key_Delete:  # delete the current item
                    model.removeRow(index.row(), index.parent())
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    item: TreeItem = index.internalPointer()
                    item.show_widget()
        super().keyPressEvent(event)

    def dropEvent(self, event: QDropEvent | None):
        if event is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                event.setDropAction(Qt.DropAction.CopyAction)

            super().dropEvent(event)  # process the event

            self.model().layoutChanged.emit()  # type: ignore


class OptionsTreeView(QTreeView):
    """Custom QTreeView containing the options for the sequence."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        # TODO: do not do the path like this
        model = TreeModel.from_file("Options", "initialization/options.json")
        self.setModel(model)

        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
