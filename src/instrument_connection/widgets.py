from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from custom_widgets.label import Label  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet, to_str, to_color  # ../instruments.py
from utility.layouts import add_sublayout, add_to_layout  # ../utility
from .ports import get_ports_list
from .constants import PORTS_FILE
from os import path


class InstrumentConnectionWidget(GroupBox):
    MAX_COMBOBOX_ITEMS = 500
    NULL_TEXT = "------------------------"

    """Widget for changing the instrument connection ports."""

    def __init__(self, instruments: InstrumentSet):
        """:param instruments: Container for instruments."""
        super().__init__("Instrument Connections", QHBoxLayout, instruments)

        self.create_widgets()

        # check the oven's connection on an interval
        self.connect_signals()
        self.instruments.oven.start()
        self.load_ports()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.oven_combobox = ComboBox()
        # add all available COM ports to the list
        self.oven_combobox.addItems(get_ports_list())
        self.oven_connection_label = Label(self.NULL_TEXT)

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
        self.oven_combobox.activated.connect(self.update_port)
        self.oven_combobox.activated.connect(self.save_ports)
        self.oven_combobox.pressed.connect(self.update_comboboxes)
        self.instruments.oven.connectionChanged.connect(self.handle_connection_change)

    def update_comboboxes(self):
        """Update the port comboboxes to show the ports that currently exist."""
        text = self.oven_combobox.currentText()
        self.oven_combobox.blockSignals(True)
        self.oven_combobox.clear()
        self.oven_combobox.addItems(get_ports_list())
        self.oven_combobox.setCurrentText(text)
        self.oven_combobox.blockSignals(False)
        # NOTE: when adding additional instruments, make sure they can never use the same port

    def update_connection_label(self, connected: bool):
        """Update the connection status label's text and color."""
        text = to_str(connected)
        self.oven_connection_label.setText(text)
        # this is HTML syntax
        self.oven_connection_label.setStyleSheet("color: " + to_color(connected))

    def handle_connection_change(self, connected: bool):
        self.update_connection_label(connected)

    def update_port(self, index: int | None = None):
        """Update the oven's port (this is a slot)."""
        self.instruments.oven.update_port(self.oven_combobox.currentText())

    def save_ports(self, index: int):
        """Writes the current port selections to a file."""
        port = self.oven_combobox.currentText()
        with open(PORTS_FILE, "w") as f:
            f.write(port)

    def load_ports(self):
        """Loads saved port selections."""
        if path.exists(PORTS_FILE):
            with open(PORTS_FILE, "r") as f:
                port = f.read()
            # if the combobox contains the previously stored port
            if self.oven_combobox.findText(port) != -1:
                self.oven_combobox.setCurrentText(port)
                self.instruments.oven.update_port(port)
