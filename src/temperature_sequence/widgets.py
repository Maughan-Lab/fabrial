from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton, QTableView
from PyQt6.QtCore import Qt
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.add_sublayout import add_sublayout  # ../helper_functions
from helper_functions.new_timer import new_timer  # ../helper_functions
from polars import col
import polars as pl
from .TableModel import TableModel
from .constants import (
    CYCLE_COLUMN,
    TEMPERATURE_COLUMN,
    BUFFER_HOURS_COLUMN,
    BUFFER_MINUTES_COLUMN,
    HOLD_HOURS_COLUMN,
    HOLD_MINUTES_COLUMN,
)


class SequenceWidget(QGroupBox):
    """
    Widget for running temperature sequences.

    :param instruments: Container for instruments.
    """

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Temperature Sequence")

        # data
        self.sequence_data = pl.DataFrame(
            # converts a dictionary into a Polars DataFrame
            {
                CYCLE_COLUMN: [],
                TEMPERATURE_COLUMN: [],
                BUFFER_HOURS_COLUMN: [],
                BUFFER_MINUTES_COLUMN: [],
                HOLD_HOURS_COLUMN: [],
                HOLD_MINUTES_COLUMN: [],
            }
        )

        # manage the layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.connect_widgets()

        # variables
        self.running = False
        self.pause = False
        self.cancel = False
        self.cycle_number = 0

        self.update_timer = new_timer(0, self.update)  # timer to update the widgets

        self.update()
        self.setFixedSize(self.sizeHint())  # make sure expanding the window behaves correctly

    def create_widgets(self, layout: QVBoxLayout):
        """Create subwidgets."""
        layout.addWidget(Label("Cycle Count"))
        self.cycle_combobox = ComboBox()
        self.cycle_combobox.addItems([str(i) for i in range(1, 501)])  # add entries 1-500
        layout.addWidget(self.cycle_combobox)

        # TODO: add DataFrame widgets
        # tabular widgets
        self.paremeter_table = QTableView()
        self.paremeter_table.setModel(TableModel(self.sequence_data))
        layout.addWidget(self.paremeter_table)

        self.start_button = QPushButton("Start Sequence")
        self.pause_button = QPushButton("Pause Sequence")
        self.unpause_button = QPushButton("Unpause Sequence")
        # default state is to show the start button
        self.pause_button.hide()
        self.unpause_button.hide()
        layout.addWidget(self.start_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.unpause_button)

        label_layout: QHBoxLayout = add_sublayout(layout, QHBoxLayout)
        temporary_label = Label("Cycle:")
        temporary_label.setFixedSize(temporary_label.sizeHint())
        label_layout.addWidget(temporary_label)
        self.cycle_label = Label("---")
        self.cycle_label.setStyleSheet("background-color: red")
        label_layout.addWidget(self.cycle_label)
        # NOTE: the labels are stretching to fill available space in the layout. Find a way to stop this

        # NOTE: the actual backend logic for this widget should be in another file.
        # TODO: fix the spacing for the nested layouts

    def connect_widgets(self):
        """Give widgets logic."""
        # TODO: connect the sequence buttons, start, pause, and unpause
        pass

    def update(self):
        """Update the state of dynamic widgets."""
        # TODO: make sure buttons are properly enabled/disabled
        # update label text
        self.cycle_label.setText(str(self.cycle_number) if self.running else "---")

        # update button states
        if not self.instruments.oven.connected:
            for button in (self.start_button, self.pause_button, self.unpause_button):
                button.setDisabled(True)
        else:
            for button in (self.start_button, self.pause_button, self.unpause_button):
                button.setDisabled(False)
