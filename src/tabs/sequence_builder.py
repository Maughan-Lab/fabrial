from PyQt6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
    QStackedWidget,
)
from PyQt6.QtCore import Qt
from ..utility.layouts import add_to_layout, add_sublayout
from ..sequence_builder.tree_views.sequence_builder import SequenceTreeWidget
from ..sequence_builder.tree_views.options import OptionsTreeWidget
from ..instruments import InstrumentSet
from ..custom_widgets.button import BiggerButton
from ..custom_widgets.label import Label
from ..custom_widgets.container import Container
from ..custom_widgets.separator import HSeparator
from ..enums.status import SequenceStatus
from .sequence_display import SequenceDisplayTab


class SequenceBuilderTab(QWidget):
    """Sequence tab."""

    def __init__(self, instruments: InstrumentSet, visual_widget_container: SequenceDisplayTab):
        """:param instruments: The application's instruments."""
        # data members
        self.options_tree: OptionsTreeWidget
        self.sequence_tree: SequenceTreeWidget
        self.instruments = instruments  # for convenience
        self.visual_widget_container = visual_widget_container  # another tab

        super().__init__()
        self.create_widgets()
        self.connect_signals()

    def create_widgets(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # treeviews
        treeview_layout = add_sublayout(layout, QHBoxLayout)
        self.options_tree = OptionsTreeWidget()
        self.sequence_tree = SequenceTreeWidget(self.instruments)
        add_to_layout(treeview_layout, self.options_tree, self.sequence_tree)

        runner_layout = QVBoxLayout()
        # start/pause/unpause buttons
        self.button_container = QStackedWidget()
        self.button_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        runner_layout.addWidget(self.button_container)
        SIZE_SCALARS = (4, 2)
        self.start_button = BiggerButton(
            "Start", self.sequence_tree.run_sequence, size_scalars=SIZE_SCALARS
        )
        self.pause_button = BiggerButton(
            "Pause", lambda: self.sequence_tree.pauseCommand.emit(), size_scalars=SIZE_SCALARS
        )
        self.unpause_button = BiggerButton(
            "Unpause", lambda: self.sequence_tree.unpauseCommand.emit(), size_scalars=SIZE_SCALARS
        )
        self.button_container.addWidget(self.start_button)
        self.button_container.addWidget(self.pause_button)
        self.button_container.addWidget(self.unpause_button)
        # status label
        INITIAL_STATUS = SequenceStatus.INACTIVE
        self.status_label = Label(INITIAL_STATUS.status_text()).set_color(INITIAL_STATUS.color())
        font = self.status_label.font()
        font.setPointSize(16)
        self.status_label.setFont(font)
        runner_layout.addWidget(HSeparator())
        runner_layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(
            Container(
                runner_layout,
                horizontal_size_policy=QSizePolicy.Policy.Fixed,
                vertical_size_policy=QSizePolicy.Policy.Fixed,
            ),
            alignment=Qt.AlignmentFlag.AlignHCenter,
        )

    def connect_signals(self):
        self.sequence_tree.processWidgetChanged.connect(
            self.visual_widget_container.set_central_widget
        )
        self.sequence_tree.sequenceStatusChanged.connect(self.handle_status_change)

    def handle_status_change(self, status: SequenceStatus):
        current_button: BiggerButton
        if status.is_pause():
            current_button = self.unpause_button
        elif status.is_running():
            current_button = self.pause_button
        else:  # we're not running
            current_button = self.start_button
            self.visual_widget_container.clear_layout()

        self.button_container.setCurrentWidget(current_button)
        self.status_label.setText(status.status_text())
        self.status_label.setStyleSheet("color: " + status.color())
