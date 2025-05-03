import json

from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from ... import Files
from ...classes.actions import Shortcut
from ...custom_widgets.augmented.button import FixedButton
from ...custom_widgets.container import Container
from ...utility.layouts import add_to_layout
from ..tree_model import TreeModel
from .tree_view import TreeView


class OptionsTreeView(TreeView):
    """Custom QTreeView containing the options for the sequence."""

    def __init__(self, parent: QWidget | None = None):
        model = TreeModel("Options")
        super().__init__(model)
        self.init_from_directory(Files.SequenceBuilder.OPTIONS_INITIALIZER)

        try:  # try to restore the previous view state
            self.init_view_state_from_file(Files.SavedSettings.Sequence.OPTIONS_STATE_AUTOSAVE)
        except Exception:  # if we can't load the expansion state, just expand everything
            self.expandAll()

        self.create_shortcuts()
        self.doubleClicked.connect(self.handle_double_click)

    def create_shortcuts(self):
        Shortcut(
            self, "Ctrl+C", self.copy_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

    def handle_double_click(self, index: QModelIndex):
        self.model().item(index).widget().show_disabled()


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
        self.view = OptionsTreeView(self)
        self.expand_button = FixedButton("Toggle Expansion")
        self.expand_button.setCheckable(True)
        self.expand_button.toggle()  # assume that the view starts mostly expanded
        self.expand_button.toggled.connect(self.handle_button_press)
        add_to_layout(layout, self.expand_button, self.view)

    def handle_button_press(self, checked: bool):
        if checked:  # expand when pressed
            self.view.expandAll()
        else:  # un-expand when unpressed
            self.view.collapseAll()

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        view_state_dict = self.view.get_view_state()
        with open(Files.SavedSettings.Sequence.OPTIONS_STATE_AUTOSAVE, "w") as f:
            json.dump(view_state_dict, f)
