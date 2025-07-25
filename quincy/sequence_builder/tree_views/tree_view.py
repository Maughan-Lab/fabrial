import json
from os import PathLike
from typing import Any, Self

from PyQt6.QtCore import QModelIndex, QPersistentModelIndex
from PyQt6.QtWidgets import QAbstractItemView, QTreeView, QWidget

from ...constants import tree_item
from ..tree_model import TreeModel

ITEM_DATA = "item-data"
VIEW_DATA = "view-data"
EXPANDED = "expanded"


class TreeView(QTreeView):
    """Custom TreeView with support for copy, cut, paste, and delete (and drag and drop)."""

    def __init__(self, model: TreeModel, parent: QWidget | None = None):
        QTreeView.__init__(self, parent)

        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setExpandsOnDoubleClick(False)
        self.setModel(model)
        self.connect_signals()

    def init_from_dict(self, data_dict: dict[str, Any]) -> Self:
        """Initialize the view from a JSON-like dictionary."""
        self.model().init_from_dict(data_dict[ITEM_DATA])
        self.init_view_state(data_dict[VIEW_DATA])
        return self

    def init_from_file(self, filepath: PathLike | str) -> Self:
        """Initialize the view from a properly formatted JSON file."""
        with open(filepath, "r") as f:
            data_dict = json.load(f)
        return self.init_from_dict(data_dict)

    def init_from_directory(self, directory_path: PathLike | str) -> Self:
        """Initialize the view from a properly formatted directory."""
        self.model().init_from_directory(directory_path)
        return self

    def init_view_state(self, view_state_dict: dict[str, Any]):
        """Recursively set the view state based on **view_state_dict**."""
        model = self.model()

        def recursively_init_state(index: QModelIndex, view_state_dict: dict[str, Any]):
            if view_state_dict[EXPANDED]:
                self.expand(index)
            children_data: list[dict[str, Any]] = view_state_dict[tree_item.CHILDREN]
            for i, child_expansion_dict in enumerate(children_data):
                child_index = model.index(i, 0, index)
                recursively_init_state(child_index, child_expansion_dict)

        recursively_init_state(self.rootIndex(), view_state_dict)

    def init_view_state_from_file(self, path: PathLike | str):
        """Initialize the view state from a file."""
        with open(path, "r") as f:
            view_state_dict = json.load(f)
        self.init_view_state(view_state_dict)

    @classmethod
    def from_file(cls: type[Self], name: str, filepath: str) -> Self:
        """
        Parameters
        ----------
        name
            The name displayed on top of the widget.
        filepath
            The filepath to build the `TreeView` from.
        """
        model = TreeModel(name)
        tree_view = cls(model).init_from_file(filepath)
        return tree_view

    def get_view_state(self) -> dict[str, Any]:
        """Get the view state as a JSON-style dictionary."""
        model = self.model()

        def get_state(index: QModelIndex) -> dict[str, Any]:
            view_state_dict: dict[str, Any] = {EXPANDED: self.isExpanded(index)}
            children_states = []
            for i in range(model.rowCount(index)):
                child_index = model.index(i, 0, index)
                children_states.append(get_state(child_index))
            view_state_dict[tree_item.CHILDREN] = children_states
            return view_state_dict

        return get_state(self.rootIndex())

    def to_dict(self) -> dict[str, Any]:
        """Convert this view's data to a JSON dictionary."""
        view_data = {
            ITEM_DATA: self.model().to_dict(),
            VIEW_DATA: self.get_view_state(),
        }
        return view_data

    def to_file(self, filepath: PathLike | str):
        """Save this view's data to a file."""
        with open(filepath, "w") as f:
            json.dump(self.to_dict(), f)

    def connect_signals(self) -> Self:
        """Connect signals."""
        self.expanded.connect(self.model().expand_event)
        self.collapsed.connect(self.model().collapse_event)
        self.doubleClicked.connect(self.show_item_widget)
        return self

    def model(self) -> TreeModel:
        """Get this view's associated model."""
        return QTreeView.model(self)  # type: ignore

    def copy_event(self) -> Self:
        """Copy items to the clipboard."""
        self.model().copy_items(self.selectedIndexes())
        return self

    def cut_event(self) -> Self:
        """Move items to the clipboard."""
        self.copy_event()
        self.delete_event()
        return self

    def paste_event(self) -> Self:
        """Paste items from the clipboard after the currently selected item."""
        self.model().paste_items(self.currentIndex())
        return self

    def delete_event(self) -> Self:
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
                    return self

        self.setCurrentIndex(new_selection_index)
        return self

    def show_item_widget(self, index: QModelIndex):
        """Show an item's widget."""
        model = self.model()
        item = model.item(index)
        item.show_widget(model.is_enabled())
