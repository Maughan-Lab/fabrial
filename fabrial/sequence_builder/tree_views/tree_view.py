from __future__ import annotations

import json
import logging
import typing
from collections.abc import Iterable, Mapping, Sequence
from os import PathLike
from typing import Self

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtWidgets import QAbstractItemView, QTreeView

from ...classes import Shortcut
from ...constants.sequence_builder import SUBITEMS
from ...utility.serde import Json
from ..tree_models.tree_model import TreeModel

EXPANDED = "expanded"


class TreeView[Model: TreeModel](QTreeView):  # type: ignore
    """Custom TreeView with support for copy, cut, paste, and delete (and drag and drop)."""

    def __init__(self, model: Model):
        QTreeView.__init__(self)

        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setExpandsOnDoubleClick(False)
        self.setModel(model)
        self.connect_signals()
        self.create_shortcuts()

    def create_shortcuts(self) -> Self:
        """Create shortcuts at construction."""
        Shortcut(
            self, "Ctrl+C", self.copy_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )
        return self

    def items_editable(self) -> bool:
        """Whether the items are editable."""
        return False

    def init_view_state_from_json(self, file: PathLike[str] | str) -> bool:
        """
        Recursively set the view state based on the contents of **file**. Returns whether the
        operation succeeded. Logs errors.
        """
        model = self.model()

        # initialize the view states of all subitems of **index**
        def recursively_init_state(index: QModelIndex, view_states: Sequence[Mapping[str, Json]]):
            for i, subitem_view_state in enumerate(view_states):
                subitem_index = model.index(i, 0, index)
                if subitem_view_state[EXPANDED]:
                    self.expand(subitem_index)
                recursively_init_state(
                    subitem_index,
                    typing.cast(Sequence[Mapping[str, Json]], subitem_view_state[SUBITEMS]),
                )

        try:
            with open(file) as f:
                view_states: Sequence[Mapping[str, Json]] = json.load(f)
            recursively_init_state(self.rootIndex(), view_states)
            return True
        except Exception:
            logging.getLogger(__name__).info(
                "Failed to initialize view state from file", exc_info=True
            )
            self.expandAll()  # just expand everything if we can't load from a file
            return False

    def save_view_state_to_json(self, file: PathLike[str] | str):
        """
        Save the view state to a JSON **file**. Returns whether the operation succeeded. Logs
        errors.
        """
        model = self.model()

        # gets the view state of all subitems
        def get_state(index: QModelIndex) -> list[dict[str, Json]]:
            subitem_states: list[dict[str, Json]] = []
            for i in range(model.rowCount(index)):
                subitem_index = model.index(i, 0, index)
                subitem_states.append(
                    {
                        EXPANDED: self.isExpanded(subitem_index),
                        SUBITEMS: get_state(subitem_index),
                    }
                )
            return subitem_states

        state = get_state(self.rootIndex())
        try:
            with open(file, "w") as f:
                json.dump(state, f)
            return True
        except Exception:
            logging.getLogger(__name__).exception("Failed to save view state to file")
            return False

    def connect_signals(self) -> Self:
        """Connect signals at construction."""
        self.expanded.connect(lambda index: self.model().expand_event(index))
        self.collapsed.connect(lambda index: self.model().collapse_event(index))
        self.doubleClicked.connect(lambda index: self.open_event([index]))
        return self

    def model(self) -> Model:  # overridden for typing
        """Get this view's associated model."""
        return typing.cast(Model, QTreeView.model(self))

    def copy_event(self):
        """Copy items to the clipboard."""
        self.model().copy_items(self.selectedIndexes())

    def open_event(self, indexes: Iterable[QModelIndex]):
        """Perform the items' "open" functions."""
        for index in indexes:
            item = self.model().get_item(index)
            if item is not None:
                if item.open_event(self.items_editable()):
                    self.setExpanded(index, not self.isExpanded(index))
