from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget

from ..constants.paths.settings import sequence as sequence_paths
from ..custom_widgets import BiggerButton, Container, HSeparator, Label
from ..enums import SequenceStatus
from ..sequence_builder import OptionsTreeWidget, SequenceTreeWidget
from ..utility import layout as layout_util
from .sequence_display import SequenceDisplayTab


class SequenceBuilderTab(QWidget):
    """Sequence tab."""

    ICON_FILE = "script-block.png"

    def __init__(self, visual_widget_container: SequenceDisplayTab):
        # data members
        self.options_tree: OptionsTreeWidget
        self.sequence_tree: SequenceTreeWidget
        self.visual_widget_container = visual_widget_container  # another tab

        QWidget.__init__(self)
        self.create_widgets()
        self.connect_signals()

    def create_widgets(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # tree views
        treeview_layout = layout_util.add_sublayout(layout, QHBoxLayout())
        self.options_tree = OptionsTreeWidget.from_initialization_directories()
        self.sequence_tree = SequenceTreeWidget.from_json(sequence_paths.SEQUENCE_AUTOSAVE_FILE)
        layout_util.add_to_layout(treeview_layout, self.options_tree, self.sequence_tree)

        runner_layout = QVBoxLayout()
        # start/pause/unpause buttons
        self.button_container = QStackedWidget()
        self.button_container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        runner_layout.addWidget(self.button_container)
        SIZE_SCALARS = (4, 2)
        self.start_button = BiggerButton(
            "Start", self.sequence_tree.run_sequence, size_scalars=SIZE_SCALARS
        )
        self.start_button.setEnabled(self.sequence_tree.directory_is_valid())
        self.pause_button = BiggerButton(
            "Pause", self.sequence_tree.command_signals.pauseCommand.emit, size_scalars=SIZE_SCALARS
        )
        self.unpause_button = BiggerButton(
            "Unpause",
            self.sequence_tree.command_signals.unpauseCommand.emit,
            size_scalars=SIZE_SCALARS,
        )
        for widget in (
            self.start_button,
            self.pause_button,
            self.unpause_button,
        ):
            self.button_container.addWidget(widget)
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
        self.sequence_tree.directoryChanged.connect(self.start_button.setEnabled)
        self.sequence_tree.graphSignalsChanged.connect(  # type: ignore
            self.visual_widget_container.connect_graph_signals, Qt.ConnectionType.DirectConnection
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

        self.button_container.setCurrentWidget(current_button)
        self.status_label.setText(status.status_text())
        self.status_label.setStyleSheet("color: " + status.color())

    def save_on_close(self):
        """Call this when closing the application to save settings."""
        self.options_tree.save_on_close()
        self.sequence_tree.save_on_close()
