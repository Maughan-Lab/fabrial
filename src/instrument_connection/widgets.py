from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet, ConnectionStatus, CONNECTION_COLOR_KEY  # ../instruments.py
from utility.layouts import add_sublayout, add_to_layout  # ../utility
from utility.new_timer import new_timer  # ../utility
from .ports import get_ports_list
from .constants import PORTS_FILE


class InstrumentConnectionWidget(GroupBox):
    MAX_COMBOBOX_ITEMS = 500

    """Widget for changing the instrument connection ports."""

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Instrument Connections", QHBoxLayout, instruments)

        self.create_widgets()
        self.connect_signals()
        self.load_ports()

        # check the oven's connection on an interval
        self.connection_timer = new_timer(1000, self.check_instrument_connection)
        self.check_instrument_connection()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.oven_combobox = ComboBox()
        # add "COM1" through "COM500" to the combobox
        self.oven_combobox.addItems(get_ports_list())
        self.oven_connection_label = Label()

        # this could probably be put in a for loop if more instruments are added
        inner_layout = add_sublayout(layout, QVBoxLayout)
        # the top label and combobox
        add_to_layout(inner_layout, Label("Oven Port"), self.oven_combobox)
        # the two bottom labels with the connection status
        label_layout = add_sublayout(inner_layout, QHBoxLayout)
        add_to_layout(label_layout, Label("Status:"), self.oven_connection_label)

    def connect_signals(self):
        """Give widgets logic."""
        # changing the oven combobox updates the oven port instantly
        self.oven_combobox.currentTextChanged.connect(self.instruments.oven.update_port)
        self.oven_combobox.currentTextChanged.connect(self.save_ports)
        self.oven_combobox.pressed.connect(self.update_comboboxes)
        self.instruments.oven.connectionChanged.connect(self.update_connection_label)

    def update_comboboxes(self):
        """Update the port comboboxes to show the ports that currently exist."""
        index = self.oven_combobox.currentIndex()
        self.oven_combobox.clear()
        self.oven_combobox.addItems(get_ports_list())
        self.oven_combobox.setCurrentIndex(index)
        # NOTE: when adding additional instruments, make sure they can never use the same port

    def update_connection_label(self, connected: bool):
        """Update the connection status label's text and color."""
        if connected:
            text = "CONNECTED"
            color = CONNECTION_COLOR_KEY[ConnectionStatus.CONNECTED]
        else:
            text = "DISCONNECTED"
            color = CONNECTION_COLOR_KEY[ConnectionStatus.DISCONNECTED]
        self.oven_connection_label.setText(text)
        self.oven_connection_label.setStyleSheet("color: " + color)  # this is HTML syntax

    def check_instrument_connection(self):
        """Reconnect to all instruments."""
        self.instruments.oven.connect()

    def save_ports(self, new_port: str):
        """Writes the current port selections to a file."""
        with open(PORTS_FILE, "w") as f:
            f.write(new_port)

    def load_ports(self):
        """Loads saved port selections."""
        with open(PORTS_FILE, "r") as f:
            port = f.read()
        # if the combobox contains the previously stored port
        if self.oven_combobox.findText(port) != -1:
            self.oven_combobox.setCurrentText(port)
