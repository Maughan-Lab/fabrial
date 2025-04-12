from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from .tree_view import TreeView
from ..tree_model import TreeModel
from ...custom_widgets.button import FixedButton
from ...custom_widgets.container import Container
from ...classes.actions import Shortcut
from ...utility.layouts import add_to_layout
from ... import Files


class OptionsTreeView(TreeView):
    """Custom QTreeView containing the options for the sequence."""

    def __init__(self, parent: QWidget | None = None):
        model = TreeModel.from_directory(
            "Options", Files.SequenceBuilder.OPTIONS_INITIALIZER
        ).sort_all()
        super().__init__(model)
        self.create_shortcuts()
        self.connect_signals()

    def create_shortcuts(self):
        Shortcut(
            self, "Ctrl+C", self.copy_event, context=Qt.ShortcutContext.WidgetWithChildrenShortcut
        )

    def connect_signals(self):
        self.expanded.connect(lambda index: self.model().item(index).widget().expand_event())
        self.collapsed.connect(lambda index: self.model().item(index).widget().collapse_event())


class OptionsTreeWidget(Container):
    """OptionsTreeView with buttons for expanding and un-expanding all items."""

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
        self.expand_button.toggled.connect(self.handle_button_press)
        self.expand_button.toggle()  # start with everything expanded
        add_to_layout(layout, self.expand_button, self.view)

    def handle_button_press(self, checked: bool):
        if checked:  # expand when pressed
            self.view.expand
            self.view.expandAll()
        else:  # un-expand when unpressed
            self.view.collapseAll()
