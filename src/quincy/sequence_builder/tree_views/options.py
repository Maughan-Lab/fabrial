import json

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout

from ...classes import Shortcut
from ...constants.paths.sequence_builder import OPTIONS_INITIALIZERS
from ...constants.paths.settings import sequence
from ...custom_widgets import Container, FixedButton
from ...utility import layout as layout_util
from ..tree_model import TreeModel
from .tree_view import TreeView


class OptionsTreeView(TreeView):
    """Custom QTreeView containing the options for the sequence."""

    def __init__(self):
        model = TreeModel("Options")
        super().__init__(model)
        self.init_from_directory(OPTIONS_INITIALIZERS)

        try:  # try to restore the previous view state
            self.init_view_state_from_file(sequence.OPTIONS_STATE_AUTOSAVE_FILE)
        except Exception:  # if we can't load the expansion state, just expand everything
            self.expandAll()

        self.create_shortcuts()

    def create_shortcuts(self):
        Shortcut(
            self, "Ctrl+C", self.copy_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

    def show_item_widget(self, index: QModelIndex):  # overridden
        self.model().item(index).show_widget(False)


class OptionsTreeWidget(Container):
    """OptionsTreeView with a button for expanding and un-expanding all items."""

    def __init__(self) -> None:
        super().__init__(QVBoxLayout())
        self.view: OptionsTreeView
        self.expand_button: FixedButton
        self.create_widgets()

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    def create_widgets(self):
        layout: QVBoxLayout = self.layout()  # type: ignore
        self.view = OptionsTreeView()
        self.expand_button = FixedButton("Toggle Expansion")
        self.expand_button.setCheckable(True)
        self.expand_button.toggle()  # assume that the view starts mostly expanded
        self.expand_button.toggled.connect(self.handle_button_press)
        layout_util.add_to_layout(layout, self.expand_button, self.view)

    def handle_button_press(self, checked: bool):
        if checked:  # expand when pressed
            self.view.expandAll()
        else:  # un-expand when unpressed
            self.view.collapseAll()

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        view_state_dict = self.view.get_view_state()
        with open(sequence.OPTIONS_STATE_AUTOSAVE_FILE, "w") as f:
            json.dump(view_state_dict, f)
