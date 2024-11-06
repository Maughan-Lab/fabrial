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
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.layouts import add_sublayout, add_to_layout  # ../helper_functions
from helper_functions.new_timer import new_timer  # ../helper_functions
from enums.stability_check_status import StabilityCheckStatus  # ../enums
from polars import col
import polars as pl
from .table_model import TableModel, TableView
from .constants import (
    CYCLE_COLUMN,
    TEMPERATURE_COLUMN,
    BUFFER_HOURS_COLUMN,
    BUFFER_MINUTES_COLUMN,
    HOLD_HOURS_COLUMN,
    HOLD_MINUTES_COLUMN,
)


class SequenceWidget(GroupBox):
    """Widget for running temperature sequences."""

    # TODO: make use of these signals for things like updating the Active/Inactive label

    # custom signals for this class
    newDataAquired = pyqtSignal(float, float)
    cycleNumberChanged = pyqtSignal(int)
    stabilityStatusChanged = pyqtSignal(StabilityCheckStatus)
    sequenceStatusChanged = pyqtSignal(bool)

    def __init__(self, instruments: InstrumentSet):
        """
        :param instruments: Container for instruments.

        :param graph_widget: A **GraphWidget** to connect to this **SequenceWidget**.
        """
        super().__init__("Temperature Sequence", QVBoxLayout, instruments)

        # variables
        self.running = False
        self.cycle_number = 0

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
        label_layout = add_sublayout(layout, QHBoxLayout, QSizePolicy.Policy.Fixed)
        self.cycle_label = Label("---")
        add_to_layout(label_layout, Label("Cycle:"), self.cycle_label)

        # separator
        layout.addWidget(HSeparator())

        # label to indicate if a sequence is active
        self.status_label = Label("Inactive")
        self.status_label.setFont(QFont("Arial", 16))  # default font is Arial
        layout.addWidget(self.status_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # NOTE: the actual backend logic for this widget should be in another file.

    def connect_signals(self):
        """Give widgets logic."""
        # TODO: connect the sequence buttons, start, pause, and unpause
        # changing the combobox will update the parameter table
        self.cycle_combobox.currentTextChanged.connect(self.update_parameter_table)
        # the running status of the sequence automatically updates the status label
        self.sequenceStatusChanged.connect(self.update_sequence_status_label)

    def update_cycle_number(self, cycle_number: int):
        self.cycle_label.setText(str(cycle_number))
        self.cycleNumberChanged.emit(cycle_number)
        # TODO: any time you update a variable connected to a signal, emit that signal

    def update_parameter_table(self, new_row_count: str):
        self.model.resize(int(new_row_count))

    def update_sequence_status_label(self, running: bool):
        # update label text
        if running:
            status_text = "Active"
            status_color = "green"
        else:
            status_text = "Inactive"
            status_color = "gray"
        self.status_label.setText(status_text)
        self.status_label.setStyleSheet("color: " + status_color)

    def update(self):
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
        if not self.instruments.oven.connected:
            for button in (self.start_button, self.pause_button, self.unpause_button):
                button.setDisabled(True)
        else:
            for button in (self.start_button, self.pause_button, self.unpause_button):
                button.setDisabled(False)
