from collections.abc import Iterable
from typing import Self

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout

from ...constants.paths.settings import sequence as sequence_paths
from ...custom_widgets import Container, FixedButton
from ...utility import layout as layout_util
from ..tree_items import CategoryItem
from ..tree_models import OptionsModel
from .tree_view import TreeView


class OptionsTreeView(TreeView[OptionsModel]):
    """`TreeView` containing item options for the sequence."""

    @classmethod
    def from_items(cls, items: Iterable[CategoryItem]) -> Self:
        """Create from the application's available plugins."""
        view = cls(OptionsModel(items))
        view.init_view_state_from_json(sequence_paths.OPTIONS_STATE_FILE)
        return view

    def save_on_close(self):
        """Call this when the application closes to save the view state."""
        self.save_view_state_to_json(sequence_paths.OPTIONS_STATE_FILE)

    def keyPressEvent(self, event: QKeyEvent | None):  # overridden
        if event is not None:
            match event.key():
                case Qt.Key.Key_Return | Qt.Key.Key_Enter:
                    self.open_event(self.selectedIndexes())
        TreeView.keyPressEvent(self, event)


class OptionsTreeWidget(Container):
    """OptionsTreeView with a button for expanding and un-expanding all items."""

    def __init__(self, view: OptionsTreeView):
        layout = QVBoxLayout()
        Container.__init__(self, layout)
        self.view = view
        self.expand_button = FixedButton("Toggle Expansion")
        self.expand_button.setCheckable(True)
        self.expand_button.toggled.connect(
            lambda checked: self.view.expandAll() if checked else self.view.collapseAll()
        )
        layout_util.add_to_layout(layout, self.expand_button, self.view)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    @classmethod
    def from_items(cls, items: Iterable[CategoryItem]) -> Self:
        """Create from the application's available plugins."""
        return cls(OptionsTreeView.from_items(items))

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        self.view.save_on_close()
