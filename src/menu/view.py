from PyQt6.QtWidgets import QMenu, QMenuBar
from ..classes.actions import Action
from ..tabs.oven_control import OvenControlTab
from ..tabs.tab_widget import TabWidget
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_window import MainWindow


class ViewMenu(QMenu):
    """View menu."""

    def __init__(self, parent: QMenuBar, main_window: "MainWindow"):
        self.pop_graph: Action

        super().__init__("&View", parent)
        self.create_actions(main_window.oven_control_tab)

        self.addAction(Action(parent, "Fullscreen", main_window.toggle_fullscreen, shortcut="F11"))
        self.addAction(
            Action(
                parent,
                "Shrink",
                main_window.shrink,
                shortcut="Ctrl+Shift+D",
            )
        )

        self.addSeparator()

        self.addAction(self.pop_graph)

    def create_actions(self, oven_control_tab: OvenControlTab):
        self.pop_graph = Action(
            oven_control_tab,
            "Pop Sequence Graph",
            lambda is_checked: (
                oven_control_tab.pop_graph() if is_checked else oven_control_tab.unpop_graph()
            ),
            shortcut="Ctrl+G",
        )
        self.pop_graph.setCheckable(True)

    def handle_popped_graph_destruction(self):
        """Uncheck the Pop Graph option without triggering signals."""
        self.pop_graph.blockSignals(True)
        self.pop_graph.setChecked(False)
        self.pop_graph.blockSignals(False)

    def handle_tab_change(self, tab_widget: TabWidget):
        oven_control_tab: OvenControlTab = self.pop_graph.parent()  # type: ignore
        self.pop_graph.setEnabled(tab_widget.currentWidget() is oven_control_tab)
