from PyQt6.QtCore import Qt, QModelIndex, QItemSelectionModel
from PyQt6.QtGui import QKeyEvent, QDropEvent
from PyQt6.QtWidgets import QTreeView, QWidget, QAbstractItemView, QVBoxLayout, QHBoxLayout
from .tree_item import TreeItem
from .tree_model import TreeModel
from ..custom_widgets.container import Container
from ..custom_widgets.button import HiddenButton
from ..utility.layouts import add_sublayout, add_to_layout


class TreeWidget(Container):
    """Custom TreeView with support for copy, cut, paste, and delete."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(QVBoxLayout)
        # add buttons
        self.create_buttons()
        # initialize the view
        self.view = QTreeView(self)
        self.view.setDragEnabled(True)
        self.view.setDropIndicatorShown(True)
        layout: QVBoxLayout = self.layout()  # type: ignore
        layout.addWidget(self.view)

    def create_buttons(self):
        layout: QVBoxLayout = self.layout()  # type: ignore
        button_layout = add_sublayout(layout, QHBoxLayout)
        # NOTE: the visibility of these buttons is what determines whether the view supports
        # cut/copy/paste/delete, since the button visibility and operation support need to always be
        # in sync
        self.copy_button = HiddenButton("Copy")
        self.cut_button = HiddenButton("Cut")
        self.paste_button = HiddenButton("Paste")
        self.delete_button = HiddenButton("Delete")
        add_to_layout(
            button_layout, self.copy_button, self.cut_button, self.paste_button, self.delete_button
        )

    def set_model(self, model: TreeModel):
        """
        Set the view's model and connect it's button signals. This should only be called once.
        """
        self.view.setModel(model)
        # TODO: connect button signals

    def set_copy_enabled(self, enabled: bool):
        """Set whether the view supports copying elements."""
        self.copy_button.setVisible(enabled)

    def copy_enabled(self) -> bool:
        """Whether the view supports copying elements."""
        return self.copy_button.isVisible()

    def set_cut_enabled(self, enabled: bool):
        """Set whether the view supports cutting elements."""
        self.cut_button.setVisible(enabled)

    def cut_enabled(self) -> bool:
        """Whether the view supports cutting elements."""
        return self.cut_button.isVisible()

    def set_paste_enabled(self, enabled: bool):
        """Set whether the view supports pasting elements."""
        self.paste_button.setVisible(enabled)

    def paste_enabled(self) -> bool:
        """Whether the view supports pasting elements."""
        return self.paste_button.isVisible()

    def set_delete_enabled(self, enabled: bool):
        """Set whether the view supports deleting elements."""
        self.delete_button.setVisible(enabled)

    def delete_enabled(self) -> bool:
        """Whether the view supports deleting elements."""
        return self.delete_button.isVisible()


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
