from PyQt6.QtWidgets import QHBoxLayout, QWidget
from ..utility.layouts import add_sublayout, add_to_layout
from ..sequence_builder.tree_view import SequenceTreeWidget, OptionsTreeWidget
from ..instruments import InstrumentSet


class SequenceTab(QWidget):
    """Sequence tab."""

    def __init__(self, parent: QWidget, instruments: InstrumentSet):
        """
        :param parent: This widget's parent.
        :param instruments: The application's instruments.
        """
        # data members
        self.options_tree: OptionsTreeWidget
        self.sequence_tree: SequenceTreeWidget
        self.instruments = instruments  # for convenience

        super().__init__(parent)
        self.create_widgets()

    def create_widgets(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        sequence_layout = add_sublayout(layout, QHBoxLayout)
        self.options_tree = OptionsTreeWidget(self)
        self.sequence_tree = SequenceTreeWidget(self, self.instruments)
        add_to_layout(sequence_layout, self.options_tree, self.sequence_tree)

    def connect_signals(self):
        pass
