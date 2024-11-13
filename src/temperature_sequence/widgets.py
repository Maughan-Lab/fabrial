from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from custom_widgets.separator import HSeparator
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.layouts import add_sublayout, add_to_layout  # ../helper_functions
from enums.status import (
    StabilityStatus,
    SequenceStatus,
    STABILITY_TEXT_KEY,
    SEQUENCE_TEXT_KEY,
    STABILITY_COLOR_KEY,
    SEQUENCE_COLOR_KEY,
)  # ../enums
from .table_model import TableModel, TableView


class SequenceWidget(GroupBox):
    """Widget for running temperature sequences."""

    # signals
    newDataAquired = pyqtSignal(float, float)
    cycleNumberChanged = pyqtSignal(int)
    stabilityChanged = pyqtSignal(StabilityStatus)
    statusChanged = pyqtSignal(SequenceStatus)
    # this widget receives the first signal and sends back the second signal
    skipBuffer = pyqtSignal()
    bufferSkipped = pyqtSignal()
    skipCycle = pyqtSignal()
    cycleSkipped = pyqtSignal()

    cancelSequence = pyqtSignal()
    sequenceStatusChanged = pyqtSignal(bool)  # True if running else False

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

        self.statusChanged.emit(SequenceStatus.INACTIVE)

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
        self.stability_label = Label(STABILITY_TEXT_KEY[StabilityStatus.NULL])
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
        self.cycle_combobox.currentTextChanged.connect(
            lambda new_row_count: self.model.resize(int(new_row_count))
        )
        # TODO: connect the sequence buttons, start, pause, and unpause

    def connect_signals(self):
        """Connect external signals."""
        # cycleNumberChanged
        self.cycleNumberChanged.connect(self.handle_cycle_number_change)
        # statusChanged
        self.statusChanged.connect(self.handle_sequence_status_change)
        # stabilityChanged
        self.stabilityChanged.connect(self.handle_stability_status_change)

        # oven connection
        self.instruments.oven.connectionChanged.connect(
            lambda connected: self.update_button_states(connected, self.instruments.oven.unlocked)
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
        self.update_cycle_number(cycle_number)
        self.limit_parameters(cycle_number)

    def update_cycle_number(self, cycle_number: int):
        self.cycle_label.setText(str(cycle_number))

    def limit_parameters(self, cycle_number):
        self.cycle_combobox.model().item(cycle_number - 2).setEnabled(False)
        self.model.disable_rows(cycle_number)

    # ----------------------------------------------------------------------------------------------
    # statusChanged
    def handle_sequence_status_change(self, status: SequenceStatus):
        match status:
            case SequenceStatus.ACTIVE:
                # tell the rest of the program the sequence started
                pass
            case SequenceStatus.COMPLETED | SequenceStatus.CANCELED | SequenceStatus.INACTIVE:
                # tell the rest of the program the sequence ended
                pass
            case _:
                pass

        self.update_label(self.status_label, SEQUENCE_TEXT_KEY[status], SEQUENCE_COLOR_KEY[status])

    # ----------------------------------------------------------------------------------------------
    # stabilityChanged
    def handle_stability_status_change(self, status: StabilityStatus):
        self.update_label(
            self.stability_label, STABILITY_TEXT_KEY[status], STABILITY_COLOR_KEY[status]
        )

    # ----------------------------------------------------------------------------------------------
    # statusChanged for SequenceStatus.Completed
    def handle_sequence_completion(self):
        self.unlimit_parameters()
        # TODO: finish this
        pass

    def unlimit_parameters(self):
        cycle_combobox_model = self.cycle_combobox.model()
        for i in range(self.cycle_combobox.count()):
            cycle_combobox_model.item(i).setEnabled(True)

        self.model.enable_all_rows()

    # ----------------------------------------------------------------------------------------------
    def update_label(self, label: Label, text: str, color: str):
        label.setText(text)
        label.setStyleSheet("color: " + color)

    def update_button_states(self, connected: bool, unlocked: bool):
        """Update the states of buttons."""
        self.start_button.setEnabled(connected and unlocked)
        self.unpause_button.setEnabled(connected)

    # ----------------------------------------------------------------------------------------------
    # sequence
    def start_sequence(self):
        pass

    def is_running(self) -> bool:
        return False
