from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout
from ..custom_widgets.label import Label
from ..custom_widgets.combo_box import ComboBox
from ..custom_widgets.groupbox import GroupBox
from ..instruments import INSTRUMENTS
from ..enums.status import ConnectionStatus
from ..utility.layouts import add_sublayout, add_to_layout
from .ports import get_ports_list
from os import path
from .. import Files


class InstrumentConnectionWidget(GroupBox):
    """Widget for changing the instrument connection ports."""

    MAX_COMBOBOX_ITEMS = 500
    NULL_TEXT = "------------"

    def __init__(self):
        super().__init__("Instrument Connection", QHBoxLayout())
        self.oven = INSTRUMENTS.oven

        self.create_widgets()

        # check the oven's connection on an interval
        self.connect_signals()
        self.oven.start()
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
        label_layout = add_sublayout(inner_layout, QFormLayout)
        label_layout.addRow("Status:", self.oven_connection_label)

    def connect_signals(self):
        """Give widgets logic."""
        # changing the oven combobox updates the oven port instantly
        self.oven_combobox.activated.connect(self.update_port)
        self.oven_combobox.activated.connect(self.save_ports)
        self.oven_combobox.pressed.connect(self.update_comboboxes)
        self.oven.connectionChanged.connect(self.handle_connection_change)

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
        text = ConnectionStatus.bool_to_str(connected)
        self.oven_connection_label.setText(text)
        # this is HTML syntax
        self.oven_connection_label.setStyleSheet(
            "color: " + ConnectionStatus.bool_to_color(connected)
        )

    def handle_connection_change(self, connected: bool):
        self.update_connection_label(connected)

    def update_port(self, index: int | None = None):
        """Update the oven's port (this is a slot)."""
        self.oven.set_port(self.oven_combobox.currentText())

    def save_ports(self, index: int):
        """Writes the current port selections to a file."""
        port = self.oven_combobox.currentText()
        with open(Files.InstrumentConnection.PORTS, "w") as f:
            f.write(port)

    def load_ports(self):
        """Loads saved port selections."""
        if path.exists(Files.InstrumentConnection.PORTS):
            with open(Files.InstrumentConnection.PORTS, "r") as f:
                port = f.read()
            # if the combobox contains the previously stored port
            if self.oven_combobox.findText(port) != -1:
                self.oven_combobox.setCurrentText(port)
                self.oven.set_port(port)
