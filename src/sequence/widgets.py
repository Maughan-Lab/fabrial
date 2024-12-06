from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThreadPool
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from custom_widgets.separator import HSeparator
from custom_widgets.dialog import OkDialog
from instruments import InstrumentSet  # ../instruments.py
from utility.layouts import add_sublayout, add_to_layout  # ../helper_functions
from enums.status import StabilityStatus, SequenceStatus  # ../enums
from .table_model import TableModel, TableView
from .sequence import SequenceThread


class SequenceWidget(GroupBox):
    """Widget for running temperature sequences."""

    # signals
    newDataAquired = pyqtSignal(float, float)
    stabilityChanged = pyqtSignal(StabilityStatus)
    statusChanged = pyqtSignal(bool)  # True if running else False
    cycleNumberChanged = pyqtSignal(int)
    # pausing
    pauseSequence = pyqtSignal()
    unpauseSequence = pyqtSignal()
    # these are commands sent from other widgets
    skipBuffer = pyqtSignal()
    skipCycle = pyqtSignal()
    cancelSequence = pyqtSignal()

    def __init__(self, instruments: InstrumentSet):
        """
        :param instruments: Container for instruments.

        :param graph_widget: A **GraphWidget** to connect to this **SequenceWidget**.
        """
        super().__init__("Temperature Sequence", QVBoxLayout, instruments)

        # variables
        self.running = False

        self.create_widgets()
        self.connect_widgets()
        self.connect_signals()

        self.handle_status_change(SequenceStatus.INACTIVE)

        self.threadpool = QThreadPool()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        # combobox
        self.cycle_combobox = ComboBox()
        self.cycle_combobox.addItems([str(i) for i in range(1, 501)])  # add entries 1-500

        # tabular widgets
        self.model = TableModel()
        self.parameter_table = TableView(self.model)

        # add the widgets
        add_to_layout(layout, Label("Cycle Count"), self.cycle_combobox, self.parameter_table)

        # buttons
        self.button_layout = add_sublayout(layout, QStackedLayout)
        self.start_button = QPushButton("Start Sequence")
        self.pause_button = QPushButton("Pause Sequence")
        self.unpause_button = QPushButton("Unpause Sequence")
        add_to_layout(self.button_layout, self.start_button, self.pause_button, self.unpause_button)

        # cycle labels
        cycle_label_layout = add_sublayout(layout, QHBoxLayout, QSizePolicy.Policy.Fixed)
        self.cycle_label = Label("---")
        add_to_layout(cycle_label_layout, Label("Cycle:"), self.cycle_label)
        # sequence status labels
        stability_label_layout = add_sublayout(layout, QHBoxLayout, QSizePolicy.Policy.Fixed)
        self.stability_label = Label(str(StabilityStatus.NULL))
        add_to_layout(stability_label_layout, Label("Stability Status:"), self.stability_label)

        # separator
        layout.addWidget(HSeparator())

        # label to indicate the status of the sequence
        self.status_label = Label()
        font = self.status_label.font()
        font.setPointSize(16)
        self.status_label.setFont(font)  # default font is Arial
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # NOTE: the actual backend logic for this widget should be in another file.

    def connect_widgets(self):
        """Connect internal widget signals."""
        # changing the combobox will update the parameter table
        self.cycle_combobox.currentIndexChanged.connect(
            lambda new_index: self.model.resize(int(new_index + 1))
        )
        self.model.dataLoaded.connect(
            lambda row_count: self.cycle_combobox.setCurrentIndexSilent(row_count - 1)
        )
        self.start_button.pressed.connect(self.start_sequence)
        self.pause_button.pressed.connect(self.pauseSequence.emit)
        self.unpause_button.pressed.connect(self.unpauseSequence.emit)

    def connect_signals(self):
        """Connect external signals."""
        # oven connection
        self.instruments.oven.connectionChanged.connect(
            lambda connected: self.update_button_states(
                connected, self.instruments.oven.is_unlocked()
            )
        )
        # oven lock
        self.instruments.oven.lockChanged.connect(
            lambda unlocked: self.update_button_states(
                self.instruments.oven.is_connected(), unlocked
            )
        )

    # ----------------------------------------------------------------------------------------------
    # cycleNumberChanged
    def handle_cycle_number_change(self, cycle_number: int):
        """Handle the cycleNumberChanged signal."""
        self.update_cycle_number(cycle_number)
        self.limit_parameters(cycle_number)
        self.cycleNumberChanged.emit(cycle_number)

    def update_cycle_number(self, cycle_number: int):
        """Update the cycle number label."""
        self.cycle_label.setText(str(cycle_number))

    def limit_parameters(self, cycle_number):
        """Limit the options in the cycle count combobox and parameters table."""
        if cycle_number > 1:
            self.cycle_combobox.model().item(cycle_number - 2).setEnabled(False)
        self.model.disable_rows(cycle_number)

    # ----------------------------------------------------------------------------------------------
    # statusChanged
    def handle_status_change(self, status: SequenceStatus):
        match status:
            case SequenceStatus.ACTIVE:
                # tell the rest of the program the sequence started
                self.statusChanged.emit(True)
                self.update_button_visibility(self.pause_button)
            case SequenceStatus.COMPLETED | SequenceStatus.CANCELED | SequenceStatus.INACTIVE:
                self.handle_sequence_completion()
                # tell the rest of the program the sequence ended
                self.statusChanged.emit(False)
            case SequenceStatus.PAUSED:
                self.update_button_visibility(self.unpause_button)
            case _:  # in case other SequenceStatus options are added
                pass
        self.update_label(self.status_label, str(status), status.to_color())

    def update_button_visibility(self, button_to_show: QPushButton):
        self.button_layout.setCurrentWidget(button_to_show)

    # ----------------------------------------------------------------------------------------------
    # stabilityChanged
    def handle_stability_change(self, status: StabilityStatus):
        self.update_label(self.stability_label, str(status), status.to_color())
        self.stabilityChanged.emit(status)

    # ----------------------------------------------------------------------------------------------
    # sequence completion
    def handle_sequence_completion(self):
        self.unlimit_parameters()
        self.update_button_visibility(self.start_button)

    def unlimit_parameters(self):
        """Remove limitations on values for the combobox and modelview."""
        cycle_combobox_model = self.cycle_combobox.model()
        for i in range(self.cycle_combobox.count()):
            cycle_combobox_model.item(i).setEnabled(True)

        self.model.enable_all_rows()

    # ----------------------------------------------------------------------------------------------
    def update_label(self, label: Label, text: str, color: str):
        """Generic function to update any label."""
        label.setText(text)
        label.setStyleSheet("color: " + color)

    def update_button_states(self, connected: bool, unlocked: bool):
        """Update the states of buttons."""
        self.start_button.setEnabled(connected and unlocked)
        self.unpause_button.setEnabled(connected)

    # ----------------------------------------------------------------------------------------------
    # sequence
    def start_sequence(self):
        """Start a temperature sequence."""
        if not self.is_running():
            thread = self.new_thread()

            thread.signals.statusChanged.connect(self.handle_status_change)
            thread.signals.stabilityChanged.connect(self.handle_stability_change)
            thread.signals.cycleNumberChanged.connect(self.handle_cycle_number_change)
            # the following gets sent to external widgets
            thread.signals.newDataAquired.connect(self.newDataAquired.emit)
            # the following are sent to the thread
            self.pauseSequence.connect(thread.pause_sequence)
            self.unpauseSequence.connect(thread.unpause_sequence)
            self.cancelSequence.connect(thread.cancel_sequence)
            self.skipCycle.connect(thread.skip_cycle)
            self.skipBuffer.connect(thread.skip_buffer)

            self.threadpool.start(thread)
        else:
            # this should never run
            OkDialog(
                "Error!", "A sequence is already running. This is a bug, please report it."
            ).exec()

    def new_thread(self):  # this is necessary for testing
        """Create a new SequenceThread."""
        return SequenceThread(self.instruments, self.model)

    def is_running(self) -> bool:
        """Determine if any SequenceThreads are active."""
        return self.threadpool.activeThreadCount() != 0
