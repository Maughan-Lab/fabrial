from PyQt6.QtWidgets import (
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from custom_widgets.separator import HSeparator
from instruments import InstrumentSet, ConnectionStatus  # ../instruments.py
from helper_functions.layouts import add_sublayout, add_to_layout  # ../helper_functions
from helper_functions.new_timer import new_timer  # ../helper_functions
from enums.status import StabilityStatus, SequenceStatus  # ../enums
from .table_model import TableModel, TableView


class SequenceWidget(GroupBox):
    """Widget for running temperature sequences."""

    # TODO: make use of these signals for things like updating the Active/Inactive label

    # custom signals
    newDataAquired = pyqtSignal(float, float)
    cycleNumberChanged = pyqtSignal(int)
    stabilityStatusChanged = pyqtSignal(StabilityStatus)
    sequenceStatusChanged = pyqtSignal(SequenceStatus)
    # this widget receives the first signal and sends back the second signal
    skipBuffer = pyqtSignal()
    bufferSkipped = pyqtSignal()
    skipCycle = pyqtSignal()
    cycleSkipped = pyqtSignal()
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
        self.connect_signals()

        self.update_timer = new_timer(0, self.update)  # timer to update the widgets
        self.update()

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
        self.stability_label = Label("-----------")
        add_to_layout(stability_label_layout, Label("Stability Status:"), self.stability_label)

        # separator
        layout.addWidget(HSeparator())

        # label to indicate the status of the sequence
        self.status_label = Label("Inactive")
        self.status_label.setFont(QFont("Arial", 16))  # default font is Arial
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # NOTE: the actual backend logic for this widget should be in another file.

    def connect_signals(self):
        """Give widgets logic."""
        # TODO: connect the sequence buttons, start, pause, and unpause
        # changing the combobox will update the parameter table
        self.cycle_combobox.currentTextChanged.connect(
            lambda new_row_count: self.model.resize(int(new_row_count))
        )

        # cycleNumberChanged
        self.cycleNumberChanged.connect(self.handle_cycle_number_change)

    # ----------------------------------------------------------------------------------------------
    def handle_cycle_number_change(self, cycle_number: int):
        self.update_cycle_number(cycle_number)
        self.limit_parameters(cycle_number)

    def update_cycle_number(self, cycle_number: int):
        self.cycle_label.setText(str(cycle_number))

    def limit_parameters(self, cycle_number):
        self.cycle_combobox.model().item(cycle_number - 2).setEnabled(False)
        self.model.disable_rows(cycle_number)
        pass

    # ----------------------------------------------------------------------------------------------
    def handle_sequence_status_change(self, status: SequenceStatus):
        match status:
            case SequenceStatus.ACTIVE:
                text = "Active"
                color = "green"
            case SequenceStatus.COMPLETED:
                text = "Completed"
                color = "gray"
            case SequenceStatus.CANCELED:
                text = "Canceled"
                color = "gray"
            case SequenceStatus.PAUSED:
                text = "Paused"
                color = "blue"
            case _:  # this should never run
                pass

        self.update_label(self.status_label, text, color)

    # ----------------------------------------------------------------------------------------------
    def handle_stability_status_change(self, status: StabilityStatus):
        match status:
            case StabilityStatus.STABLE:
                text = "Stable"
                color = "green"
            case StabilityStatus.BUFFERING:
                text = "Buffering"
                color = "blue"
            case StabilityStatus.CHECKING:
                text = "Checking..."
                color = "orange"
            case StabilityStatus.ERROR:
                text = "Error"
                color = "red"
            case _:  # this should never run
                pass

        self.update_label(self.stability_label, text, color)

    # ----------------------------------------------------------------------------------------------
    def handle_sequence_completion(self):
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

    def update(self):
        # TODO: remove this function and replace it with signals
        """Update the state of dynamic widgets."""
        # update label text
        if self.running:
            cycle_text = str(self.cycle_number + 1)
            status_text = "Active"
            status_color = "green"
        else:
            cycle_text = "---"
            status_text = "Inactive"
            status_color = "gray"
        self.cycle_label.setText(cycle_text)
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet("color: " + status_color)

        # update button states
        if not self.instruments.oven.connection_status == ConnectionStatus.CONNECTED:
            for button in (self.start_button, self.pause_button, self.unpause_button):
                button.setDisabled(True)
        else:
            for button in (self.start_button, self.pause_button, self.unpause_button):
                button.setDisabled(False)
