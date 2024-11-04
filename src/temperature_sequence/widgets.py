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
    TIME_DATA_COLUMN,
    TEMPERATURE_DATA_COLUMN,
)


class SequenceWidget(GroupBox):
    """Widget for running temperature sequences."""

    # custom signals for this class
    newDataAquired = pyqtSignal(float, float)
    cycleNumberChanged = pyqtSignal(int)
    statusChanged = pyqtSignal(StabilityCheckStatus)

    def __init__(self, instruments: InstrumentSet):
        """
        :param instruments: Container for instruments.

        :param graph_widget: A **GraphWidget** to connect to this **SequenceWidget**.
        """
        super().__init__("Temperature Sequence", QVBoxLayout, instruments)

        # data
        # TODO: remove the testing data
        self.sequence_data = pl.DataFrame(
            # converts a dictionary into a Polars DataFrame
            {
                CYCLE_COLUMN: [i for i in range(10)],
                TEMPERATURE_COLUMN: [float(i) for i in range(10)],
                BUFFER_HOURS_COLUMN: [i for i in range(10)],
                BUFFER_MINUTES_COLUMN: [i for i in range(10)],
                HOLD_HOURS_COLUMN: [i for i in range(10)],
                HOLD_MINUTES_COLUMN: [i for i in range(10)],
            }
        )
        self.temperature_data: list[float] = []

        # variables
        self.running = False
        self.cycle_number = 0

        self.create_widgets()
        self.connect_widgets()

        self.update_timer = new_timer(0, self.update)  # timer to update the widgets
        self.update()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        # combobox
        self.cycle_combobox = ComboBox()
        self.cycle_combobox.addItems([str(i) for i in range(1, 501)])  # add entries 1-500

        # tabular widgets
        self.parameter_table = TableView()
        self.parameter_table.setModel(TableModel(self.sequence_data))
        self.parameter_table.updateSize()

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

    def connect_widgets(self):
        """Give widgets logic."""
        # TODO: connect the sequence buttons, start, pause, and unpause
        pass

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
