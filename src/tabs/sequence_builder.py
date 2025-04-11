from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QStackedWidget,
)
from PyQt6.QtCore import Qt
from ..utility.layouts import add_to_layout
from ..sequence_builder.tree_view import SequenceTreeWidget, OptionsTreeWidget
from ..instruments import InstrumentSet
from ..custom_widgets.button import Button
from ..custom_widgets.label import Label
from ..custom_widgets.container import Container
from ..custom_widgets.separator import HSeparator


class SequenceBuilderTab(QWidget):
    """Sequence tab."""

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: The application's instruments."""
        # data members
        self.options_tree: OptionsTreeWidget
        self.sequence_tree: SequenceTreeWidget
        self.instruments = instruments  # for convenience

        super().__init__()
        self.create_widgets()

    def create_widgets(self):
        layout = QHBoxLayout()
        self.setLayout(layout)

        # treeviews
        self.options_tree = OptionsTreeWidget(self)
        self.sequence_tree = SequenceTreeWidget(self, self.instruments)
        add_to_layout(layout, self.options_tree, self.sequence_tree)

        runner_layout = QVBoxLayout()
        # start/pause/unpause buttons
        self.button_container = QStackedWidget()
        self.button_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        runner_layout.addWidget(self.button_container)
        self.start_button = Button("Start", self.sequence_tree.run_sequence)
        self.pause_button = Button("Pause", lambda: self.sequence_tree.set_paused(True))
        self.unpause_button = Button("Unpause", lambda: self.sequence_tree.set_paused(False))
        self.button_container.addWidget(self.start_button)
        self.button_container.addWidget(self.pause_button)
        self.button_container.addWidget(self.unpause_button)
        # status label
        self.status_label = Label("Sample Text")
        font = self.status_label.font()
        font.setPointSize(16)
        self.status_label.setFont(font)
        runner_layout.addWidget(HSeparator())
        runner_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(
            Container(runner_layout, vertical_size_policy=QSizePolicy.Policy.Fixed),
        )

    def connect_signals(self):
        pass
