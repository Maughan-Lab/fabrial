from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.layouts import add_sublayout, add_to_layout  # ../helper_functions
from helper_functions.new_timer import new_timer  # ../helper_functions


class InstrumentConnectionWidget(GroupBox):
    MAX_COMBOBOX_ITEMS = 500

    """Widget for changing the instrument connection ports."""

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Instrument Connections", QHBoxLayout, instruments)

        self.create_widgets()
        self.connect_signals()

        # check the oven's connection on an interval
        self.connection_timer = new_timer(1000, self.check_instrument_connection)
        self.check_instrument_connection()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.oven_combobox = ComboBox()
        # add "COM1" through "COM500" to the combobox
        self.oven_combobox.addItems(
            ["COM" + str(number) for number in range(self.MAX_COMBOBOX_ITEMS + 1)]
        )
        self.oven_connection_label = Label()

        # this could probably be put in a for loop if more instruments are added
        inner_layout = add_sublayout(layout, QVBoxLayout)
        # the top label and combobox
        add_to_layout(inner_layout, Label("Oven Port"), self.oven_combobox)
        # the two bottom labels with the connection status
        label_layout = add_sublayout(inner_layout, QHBoxLayout)
        add_to_layout(label_layout, Label("Status:"), self.oven_connection_label)

        # NOTE: when adding additional instruments, make sure they can never use the same port

    def connect_signals(self):
        """Give widgets logic."""
        # changing the oven combobox updates the oven port instantly
        self.oven_combobox.currentTextChanged.connect(
            lambda new_port: self.instruments.oven.update_port(new_port)
        )
        self.instruments.oven.connectionChanged.connect(self.update_connection_label)

    def update_connection_label(self, connected: bool):
        if connected:
            text = "CONNECTED"
            color = "green"
        else:
            text = "DISCONNECTED"
            color = "red"
        self.oven_connection_label.setText(text)
        self.oven_connection_label.setStyleSheet("color: " + color)  # this is HTML syntax

    def check_instrument_connection(self):
        self.instruments.oven.connect()
