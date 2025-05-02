from typing import TYPE_CHECKING

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu, QMenuBar

from ..classes.actions import Action
from ..tabs.oven_control import OvenControlTab
from ..tabs.sequence_display import SequenceDisplayTab
from ..tabs.tab_widget import TabWidget

if TYPE_CHECKING:
    from ..main_window import MainWindow


class ViewMenu(QMenu):
    """View menu."""

    def __init__(self, parent: QMenuBar, main_window: "MainWindow", graph_tab: SequenceDisplayTab):
        self.pop_graph: Action

        super().__init__("&View", parent)
        self.create_actions(graph_tab)

        self.addAction(
            Action(main_window, "Fullscreen", main_window.toggle_fullscreen, shortcut="F11")
        )
        self.addAction(
            Action(
                main_window,
                "Shrink",
                main_window.shrink,
                shortcut="Ctrl+Shift+D",
            )
        )

        self.addSeparator()

        self.addAction(self.pop_graph)

    def create_actions(self, graph_tab: SequenceDisplayTab):
        self.pop_graph = Action(
            graph_tab,
            "Pop Sequence Graph",
            lambda is_checked: (graph_tab.pop_graph() if is_checked else graph_tab.unpop_graph()),
            shortcut="Ctrl+g",
            shortcut_context=Qt.ShortcutContext.WidgetWithChildrenShortcut,
        )
        graph_tab.addAction(self.pop_graph)
        self.pop_graph.setCheckable(True)
        graph_tab.poppedGraphChanged.connect(self.handle_pop_change)

    def handle_pop_change(self, popped: bool):
        """Uncheck the Pop Graph option without triggering signals."""
        self.pop_graph.blockSignals(True)
        self.pop_graph.setChecked(popped)
        self.pop_graph.blockSignals(False)

    def handle_tab_change(self, tab_widget: TabWidget):
        return
        oven_control_tab: OvenControlTab = self.pop_graph.parent()  # type: ignore
        self.pop_graph.setEnabled(tab_widget.currentWidget() is oven_control_tab)
