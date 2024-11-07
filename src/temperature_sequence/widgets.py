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
from enums.status import StabilityStatus, SequenceStatus  # ../enums
from .table_model import TableModel, TableView


class SequenceWidget(GroupBox):
    """Widget for running temperature sequences."""

    # TODO: make use of these signals for things like updating the Active/Inactive label

    # custom signals for this class
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
        self.cycle_combobox.currentTextChanged.connect(self.update_parameter_table)

        # cycleNumberChanged
        self.cycleNumberChanged.connect(self.handle_cycle_number_change)

    # ----------------------------------------------------------------------------------------------

    def handle_cycle_number_change(self, cycle_number: int):
        self.update_cycle_number(cycle_number)
        self.limit_parameters(cycle_number)

    def update_cycle_number(self, cycle_number: int):
        self.cycle_label.setText(str(cycle_number))
        # TODO: any time you update a variable connected to a signal, emit that signal

    def limit_parameters(self, cycle_number):
        # TODO: limit the combobox options and disable parts of the model view
        pass

    # ----------------------------------------------------------------------------------------------

    def update_parameter_table(self, new_row_count: str):
        self.model.resize(int(new_row_count))

    def update_status_label(self, text: str, color: str):
        # update label text
        self.status_label.setText(text)
        self.status_label.setStyleSheet("color: " + color)

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
        if not self.instruments.oven.connected:
            for button in (self.start_button, self.pause_button, self.unpause_button):
                button.setDisabled(True)
        else:
            for button in (self.start_button, self.pause_button, self.unpause_button):
                button.setDisabled(False)
