from PyQt6.QtWidgets import QHBoxLayout, QWidget
from ..utility.layouts import add_sublayout, add_to_layout
from ..tree_model.tree_view import SequenceTreeWidget, OptionsTreeWidget


class SequenceTab(QWidget):
    """Sequence tab."""

    def __init__(self, parent: QWidget):
        # data members
        self.options_tree: OptionsTreeWidget
        self.sequence_tree: SequenceTreeWidget
        # TODO: add the graph, a start button, pause button, and any labels you need

        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        sequence_layout = add_sublayout(layout, QHBoxLayout)
        self.options_tree = OptionsTreeWidget(self)
        self.sequence_tree = SequenceTreeWidget(self)
        add_to_layout(sequence_layout, self.options_tree, self.sequence_tree)

    def connect_signals(self):
        pass
