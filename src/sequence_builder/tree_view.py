from PyQt6.QtCore import (
    Qt,
    QModelIndex,
    QItemSelectionModel,
    QPersistentModelIndex,
    QThreadPool,
    QItemSelection,
)
from PyQt6.QtGui import QKeyEvent, QDropEvent
from PyQt6.QtWidgets import QTreeView, QWidget, QAbstractItemView, QVBoxLayout
from .tree_model import TreeModel
from ..custom_widgets.button import FixedButton
from ..custom_widgets.container import Container
from ..custom_widgets.button import Button
from ..custom_widgets.label import Label
from ..classes.actions import Shortcut
from ..utility.layouts import add_to_layout, add_sublayout
from .. import Files
from typing import Self
from .sequence_runner import SequenceRunner
from ..instruments import InstrumentSet


class TreeView(QTreeView):
    """Custom TreeView with support for copy, cut, paste, and delete (and drag and drop)."""

    def __init__(self, parent: QWidget | None = None, model: TreeModel = TreeModel()):
        super().__init__(parent)
        # initialize
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setModel(model)

    def model(self) -> TreeModel:
        """Get this view's associated model."""
        return super().model()  # type: ignore

    def copy_event(self) -> None:
        """Copy items to the clipboard."""
        self.model().copy_items(self.selectedIndexes())

    def cut_event(self) -> None:
        """Move items to the clipboard."""
        self.copy_event()
        self.delete_event()

    def paste_event(self) -> None:
        """Paste items from the clipboard after the currently selected item."""
        self.model().paste_items(self.currentIndex())

    def delete_event(self) -> None:
        """Delete currently selected items."""
        # store the index below the current index
        next_selection_index = self.indexBelow(self.currentIndex())
        persistent_new_selection_index = QPersistentModelIndex(next_selection_index)

        self.model().delete_items(self.selectedIndexes())

        # select the next available item after deleting
        new_selection_index = QModelIndex(persistent_new_selection_index)
        if not new_selection_index.isValid():
            # try the item below the currently selected item
            new_selection_index = self.indexBelow(self.currentIndex())
            if not new_selection_index.isValid():
                # try whatever is currently selected (usually the last item in this situation)
                new_selection_index = self.currentIndex()
                if not new_selection_index.isValid():
                    # at this point there should be no items in the model
                    self.clearSelection()
                    return

        self.selectionModel().select(  # type: ignore
            new_selection_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )


class SequenceTreeView(TreeView):
    """Custom TreeView for displaying sequence settings."""

    def __init__(self, parent: QWidget | None = None):
        # initialize the model
        model = TreeModel("Sequence Builder")
        model.set_supported_drag_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        model.set_supported_drop_actions(Qt.DropAction.MoveAction | Qt.DropAction.CopyAction)
        # initialize the super class
        super().__init__(parent, model)
        # configure
        self.setExpandsOnDoubleClick(False)
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.doubleClicked.connect(self.handle_double_click)

        self.connect_signals()
        self.create_shortcuts()

    def connect_signals(self):
        # expand the view when drops occur so it's easier to see what changed
        self.model().dropOccurred.connect(lambda index: self.expand(index))

    def create_shortcuts(self):
        Shortcut(
            self, "Ctrl+C", self.copy_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        Shortcut(
            self, "Ctrl+X", self.cut_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        Shortcut(
            self, "Ctrl+V", self.paste_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

    def handle_double_click(self, index: QModelIndex):
        """On a double click event."""
        self.model().item(index).show_widget()  # show the selected item's widget

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def keyPressEvent(self, event: QKeyEvent | None):
        if event is not None:
            index = self.currentIndex()
            model = self.model()
            match event.key():
                case Qt.Key.Key_Delete:  # delete the current item
                    self.delete_event()
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    model.item(index).show_widget()
        super().keyPressEvent(event)

    def dropEvent(self, event: QDropEvent | None):
        if event is not None:
            if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                event.setDropAction(Qt.DropAction.CopyAction)

            super().dropEvent(event)  # process the event


class SequenceTreeWidget(Container):
    """SequenceTreeView with a delete button."""

    def __init__(self, parent: QWidget | None, instruments: InstrumentSet):
        """
        :param parent: This widget's parent.
        :param instruments: The application's instruments.
        """
        super().__init__(QVBoxLayout())
        self.setParent(parent)

        self.view: SequenceTreeView
        self.delete_button: FixedButton
        self.create_widgets().connect_signals()

        self.threadpool = QThreadPool()
        self.instruments = instruments

    def create_widgets(self) -> Self:
        layout: QVBoxLayout = self.layout()  # type: ignore
        self.view = SequenceTreeView(self)
        self.delete_button = FixedButton("Delete Selected Items", self.view.delete_event)
        self.delete_button.setEnabled(False)
        add_to_layout(layout, self.delete_button, self.view)

        # the data directory selection widgets
        directory_layout = add_sublayout(layout, QVBoxLayout)
        directory_button = Button("Choose Data Directory", self.choose_directory)
        self.directory_label = Label(
            r"C:\Users\drewl\C:\Users\drewl\C:\Users\drewl\C:\Users\drewl\C:\Users\drewl\C:\Users\drewl\C:\Users\drewl\C:\Users\drewl\C:\Users\drewl"
        )
        self.directory_label.setContentsMargins(7, 0, 7, 0)
        self.directory_label.setWordWrap(True)
        add_to_layout(directory_layout, directory_button, self.directory_label)

        return self

    def connect_signals(self) -> Self:
        self.view.selectionModel().selectionChanged.connect(self.handle_selection_change)  # type: ignore
        return self

    def handle_selection_change(self, selected: QItemSelection, *args):
        enabled = True
        if selected.isEmpty():
            enabled = False
        else:
            for index in selected.indexes():
                if not index.isValid():
                    enabled = False
        self.delete_button.setEnabled(enabled)

    def choose_directory(self):
        """Open a dialog to choose the data-storage directory."""
        # TODO: open a folder dialog and set the label to the result
        self.directory_label.setText("")

    def run_sequence(self):
        """Run the sequence."""
        runner = SequenceRunner(self.instruments, "", self.view.model().root())
        self.threadpool.start(runner)
        # TODO: connect the error signal so it can show a dialog

    def set_paused(self, paused: bool) -> Self:
        """Pause/unpause the sequence runner."""
        # TODO:
        return self

    def cancel_sequence(self) -> Self:
        # TODO
        return self

    def skip_current_process(self) -> Self:
        # TODO
        return self


class OptionsTreeView(TreeView):
    """Custom QTreeView containing the options for the sequence."""

    def __init__(self, parent: QWidget | None = None):
        model = TreeModel.from_directory(
            "Options", Files.SequenceBuilder.OPTIONS_INITIALIZER
        ).sort_all()
        super().__init__(parent, model)
        self.create_shortcuts()

    def create_shortcuts(self):
        Shortcut(
            self, "Ctrl+C", self.copy_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )


class OptionsTreeWidget(Container):
    """OptionsTreeView with buttons for expanding and un-expanding all items."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(QVBoxLayout())
        self.view: OptionsTreeView
        self.expand_button: FixedButton
        self.create_widgets()

        # self.view.setEnabled(False)
        self.s = None
        self.p = None

    def create_widgets(self):
        layout: QVBoxLayout = self.layout()  # type: ignore
        self.view = OptionsTreeView(self)
        self.expand_button = FixedButton("Toggle Expansion")
        self.expand_button.setCheckable(True)
        self.expand_button.toggled.connect(self.handle_button_press)
        add_to_layout(layout, self.expand_button, self.view)

    def handle_button_press(self, checked: bool):
        if checked:  # expand when pressed
            self.view.expandAll()
        else:  # un-expand when unpressed
            self.view.collapseAll()
