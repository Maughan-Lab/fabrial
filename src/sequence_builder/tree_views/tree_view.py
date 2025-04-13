from PyQt6.QtWidgets import QAbstractItemView, QTreeView
from PyQt6.QtCore import QModelIndex, QPersistentModelIndex, QItemSelectionModel
from ..tree_model import TreeModel
from typing import Self


class TreeView(QTreeView):
    """Custom TreeView with support for copy, cut, paste, and delete (and drag and drop)."""

    def __init__(self, model: TreeModel):
        super().__init__()

        # initialize
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setExpandsOnDoubleClick(False)
        self.setModel(model)

    def model(self) -> TreeModel:
        """Get this view's associated model."""
        return super().model()  # type: ignore

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

        self.selectionModel().select(  # type: ignore
            new_selection_index, QItemSelectionModel.SelectionFlag.ClearAndSelect
        )
        return self
