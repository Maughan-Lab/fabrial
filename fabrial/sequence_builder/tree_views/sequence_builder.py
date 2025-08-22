from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from PyQt6.QtCore import QItemSelection, QModelIndex, QPersistentModelIndex, QPoint, Qt
from PyQt6.QtGui import QDragMoveEvent, QKeyEvent
from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QVBoxLayout

from ...classes import Shortcut, Timer
from ...constants.paths.settings import sequence as sequence_paths
from ...custom_widgets import Button, Container, FixedButton, OkDialog
from ...utility import images, layout as layout_util
from ..tree_models import SequenceModel
from .tree_view import TreeView


@dataclass
class DragTracker:
    timer: Timer
    position: QPoint


class SequenceTreeView(TreeView[SequenceModel]):
    """
    Custom `TreeView` for displaying sequence settings.

    Parameters
    ----------
    model
        The model the view will use.
    """

    def __init__(self, model: SequenceModel):
        TreeView.__init__(self, model)
        # configure
        self.setAcceptDrops(True)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)

        # used to expand items when hovering over them
        point = QPoint()
        timer = Timer(self, 500, lambda: self.expand(self.indexAt(point)))
        timer.setSingleShot(True)
        self.drag_tracker = DragTracker(timer, point)

    @classmethod
    def from_autosave(cls) -> Self:
        """Create from the autosave files."""
        model = SequenceModel([])
        model.init_from_json(sequence_paths.SEQUENCE_ITEMS_FILE)
        view = cls(model)
        view.init_view_state_from_json(sequence_paths.SEQUENCE_STATE_FILE)
        return view

    def select_load(self):
        """Load sequence items from a user-selected file."""
        file, _ = QFileDialog.getOpenFileName(
            self, "Select sequence file", filter="JSON files (*.json)"
        )
        if file != "":
            if not self.model().init_from_json(file):
                OkDialog(
                    "Load Error",
                    "Failed to load the requested file. Ensure the file is correctly formatted and "
                    "that all plugins the file references are installed.",
                ).exec()
            else:
                self.expandAll()

    def select_save(self):
        """Save the sequence items to a user-selected file."""
        file, _ = QFileDialog.getSaveFileName(
            self, "Select save file", "untitled.json", "JSON files (*.json)"
        )
        if file != "":
            if not self.model().to_json(file):
                OkDialog(
                    "Save Error",
                    "Failed to save sequence. "
                    "This could be caused by a faulty plugin or permission issues. "
                    "See the error log for details.",
                ).exec()

    def save_on_close(self):
        """Call this when closing the application to save the item and view state."""
        self.model().to_json(sequence_paths.SEQUENCE_ITEMS_FILE)
        self.save_view_state_to_json(sequence_paths.SEQUENCE_STATE_FILE)

    def connect_signals(self):  # overridden
        TreeView.connect_signals(self)
        self.model().itemAdded.connect(self.handle_new_item)

    def create_shortcuts(self):  # overridden
        TreeView.create_shortcuts(self)
        Shortcut(
            self, "Ctrl+X", self.cut_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        Shortcut(
            self, "Ctrl+V", self.paste_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

    def items_editable(self) -> bool:  # overridden
        return self.model().is_enabled()

    def set_readonly(self, readonly: bool):
        """Set whether the view is read-only."""
        self.model().set_enabled(not readonly)
        self.setAcceptDrops(not readonly)
        self.setDragEnabled(not readonly)
        if readonly:
            self.clearSelection()

    def handle_new_item(self, index: QModelIndex):
        """Handle an item being added to the model."""
        self.expand(index)  # expand the new item
        self.expand(index.parent())  # and its parent

    def cut_event(self):
        """Move items to the clipboard."""
        self.copy_event()
        self.delete_event()

    def paste_event(self):
        """Paste items from the clipboard after the currently selected item."""
        self.model().paste_items(self.currentIndex())

    def delete_event(self):
        """Delete currently selected items."""
        # store the index below the current index
        persistent_new_selection_index = QPersistentModelIndex(self.indexBelow(self.currentIndex()))

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

        self.setCurrentIndex(new_selection_index)

    # ----------------------------------------------------------------------------------------------
    def keyPressEvent(self, event: QKeyEvent | None):  # overridden
        if event is not None:
            match event.key():
                case Qt.Key.Key_Delete:  # delete the current item
                    self.delete_event()
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    self.open_event(self.selectedIndexes())
        TreeView.keyPressEvent(self, event)

    def dragMoveEvent(self, event: QDragMoveEvent | None):  # overridden
        if event is not None:
            tracked_position = self.drag_tracker.position
            event_position = event.position().toPoint()
            tracked_position.setX(event_position.x())
            tracked_position.setY(event_position.y())
            self.drag_tracker.timer.start()
        TreeView.dragMoveEvent(self, event)


class SequenceTreeWidget(Container):
    """SequenceTreeView with a delete button."""

    def __init__(self, view: SequenceTreeView):
        layout = QVBoxLayout()
        Container.__init__(self, layout)

        self.view = view
        self.delete_button = Button("Delete Selected Items", self.view.delete_event)
        self.create_widgets(layout)
        self.connect_signals()

    @classmethod
    def from_autosave(cls) -> Self:
        """Create from the autosave files."""
        view = SequenceTreeView.from_autosave()
        return cls(view)

    def create_widgets(self, layout: QVBoxLayout):
        """Create widgets at construction."""
        button_layout = QHBoxLayout()
        button_container = Container(button_layout)

        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)

        button_sublayout = QHBoxLayout()
        self.save_button = FixedButton("Save", self.view.select_save)
        self.save_button.setIcon(images.make_icon("script-export.png"))
        button_sublayout.addWidget(self.save_button)
        self.load_button = FixedButton("Load", self.view.select_load)
        self.load_button.setIcon(images.make_icon("script-import.png"))
        button_sublayout.addWidget(self.load_button)

        button_layout.addWidget(self.delete_button, alignment=Qt.AlignmentFlag.AlignLeft)
        button_layout.addLayout(button_sublayout)

        layout_util.add_to_layout(layout, button_container, self.view)

    def connect_signals(self):
        """Connect signals at construction."""
        self.view.selectionModel().selectionChanged.connect(  # type: ignore
            self.handle_selection_change
        )

    def handle_selection_change(self, selected: QItemSelection, *args):
        """Handle the item selection changing."""
        enabled = True
        if selected.isEmpty():
            enabled = False
        else:
            for index in selected.indexes():
                if not index.isValid():
                    enabled = False
        self.delete_button.setEnabled(enabled)

    def set_readonly(self, readonly: bool):
        """Set whether the widget is read-only."""
        self.view.set_readonly(readonly)
        self.load_button.setDisabled(readonly)

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        self.view.save_on_close()
