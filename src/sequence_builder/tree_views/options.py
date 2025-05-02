from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtWidgets import QSizePolicy, QVBoxLayout, QWidget

from ... import Files
from ...classes.actions import Shortcut
from ...custom_widgets.button import FixedButton
from ...custom_widgets.container import Container
from ...utility.layouts import add_to_layout
from ..tree_model import TreeModel
from .tree_view import TreeView


class OptionsTreeView(TreeView):
    """Custom QTreeView containing the options for the sequence."""

    def __init__(self, parent: QWidget | None = None):
        model = TreeModel.from_directory(
            "Options", Files.SequenceBuilder.OPTIONS_INITIALIZER
        ).sort_all()
        super().__init__(model, parent)
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
        self.expand_button.toggled.connect(self.handle_button_press)
        self.expand_button.toggle()  # start with everything expanded
        add_to_layout(layout, self.expand_button, self.view)

    def handle_button_press(self, checked: bool):
        if checked:  # expand when pressed
            self.view.expandAll()
        else:  # un-expand when unpressed
            self.view.collapseAll()
