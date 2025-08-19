from PyQt6.QtWidgets import QFormLayout, QHBoxLayout, QVBoxLayout

from ..constants.paths.settings import oven as settings
from ..custom_widgets import ComboBox, GroupBox, Label
from ..enums import ConnectionStatus
from ..utility import layout as layout_util
from . import ports


class InstrumentConnectionWidget(GroupBox):
    """Widget for changing the instrument connection ports."""

    MAX_COMBOBOX_ITEMS = 500
    NULL_TEXT = "------------"

    def __init__(self):
        GroupBox.__init__(self, "Instrument Connection", QHBoxLayout())
        self.oven = INSTRUMENTS.oven

        self.create_widgets()

        # check the oven's connection on an interval
        self.connect_signals()
        self.oven.start()
        self.load_ports()

    def create_widgets(self):
        """Create subwidgets."""
        layout: QHBoxLayout = self.layout()  # type: ignore

        self.oven_combobox = ComboBox()
        # add all available COM ports to the list
        self.oven_combobox.addItems(ports.list_ports())
        self.oven_connection_label = Label(self.NULL_TEXT)

        # this could probably be put in a for loop if more instruments are added
        inner_layout = layout_util.add_sublayout(layout, QVBoxLayout())
        # the top label and combobox
        layout_util.add_to_layout(inner_layout, Label("Oven Port"), self.oven_combobox)
        # the two bottom labels with the connection status
        label_layout = layout_util.add_sublayout(inner_layout, QFormLayout())
        label_layout.addRow("Status:", self.oven_connection_label)

    def connect_signals(self):
        """Give widgets logic."""
        # changing the oven combobox updates the oven port instantly
        self.oven_combobox.activated.connect(self.update_port)
        self.oven_combobox.pressed.connect(self.update_comboboxes)
        self.oven.connectionChanged.connect(self.handle_connection_change)

    def update_comboboxes(self):
        """Update the port comboboxes to show the ports that currently exist."""
        text = self.oven_combobox.currentText()
        self.oven_combobox.blockSignals(True)
        self.oven_combobox.clear()
        self.oven_combobox.addItems(ports.list_ports())
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

    def save_on_close(self):
        """Call this when closing the application to save the oven port."""
        port = self.oven_combobox.currentText()
        with open(settings.OVEN_PORT_FILE, "w") as f:
            f.write(port)

    def load_ports(self):
        """Loads saved port selections."""
        try:
            with open(settings.OVEN_PORT_FILE, "r") as f:
                port = f.read().strip()
            # if the combobox contains the previously stored port
            if self.oven_combobox.findText(port) != -1:
                self.oven_combobox.setCurrentText(port)
                self.oven.set_port(port)
        except Exception:
            pass
