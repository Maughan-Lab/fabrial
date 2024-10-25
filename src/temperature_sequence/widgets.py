from PyQt6.QtWidgets import (
    QGroupBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QStackedLayout,
    QSizePolicy,
)
from custom_widgets.label import Label, FixedLabel  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.layouts import add_sublayout, add_to_layout  # ../helper_functions
from helper_functions.new_timer import new_timer  # ../helper_functions
from polars import col
import polars as pl
from .TableModel import TableModel, TableView
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

        # manage the layout
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
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

    def create_widgets(self, layout: QVBoxLayout):
        """Create subwidgets."""
        # combobox
        self.cycle_combobox = ComboBox()
        self.cycle_combobox.addItems([str(i) for i in range(1, 501)])  # add entries 1-500
        # tabular widgets
        self.parameter_table = TableView()
        self.parameter_table.setModel(TableModel(self.sequence_data))
        self.parameter_table.updateSize()
        # add the widgets
        add_to_layout(layout, FixedLabel("Cycle Count"), self.cycle_combobox, self.parameter_table)
        # buttons
        self.button_layout: QStackedLayout = add_sublayout(layout, QStackedLayout)
        self.start_button = QPushButton("Start Sequence")
        self.pause_button = QPushButton("Pause Sequence")
        self.unpause_button = QPushButton("Unpause Sequence")
        add_to_layout(self.button_layout, self.start_button, self.pause_button, self.unpause_button)
        # cycle labels
        label_layout: QHBoxLayout = add_sublayout(layout, QHBoxLayout)
        self.cycle_label = Label("---")
        add_to_layout(label_layout, FixedLabel("Cycle:"), self.cycle_label)

        # NOTE: the actual backend logic for this widget should be in another file.

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


# TODO: need to resize the frame when the table is resized
