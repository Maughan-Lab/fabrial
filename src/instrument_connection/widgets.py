from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout
from custom_widgets.label import Label # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.layouts import add_sublayout, add_to_layout  # ../helper_functions
from helper_functions.new_timer import new_timer  # ../helper_functions

MAX_COMBOBOX_ITEMS = 500


class InstrumentConnectionWidget(GroupBox):
    """
    Widget for changing the instrument connection ports.

    :param instruments: Container for instruments.
    """

    def __init__(self, instruments: InstrumentSet):
        super().__init__("Instrument Connections", QHBoxLayout, instruments)

        self.create_widgets()
        self.connect_widgets()

        # timer to check the connection of the instruments every few seconds
        self.update_timer = new_timer(3000, self.update)

        self.update()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        self.oven_combobox = ComboBox()
        # add "COM1" through "COM500" to the combobox
        self.oven_combobox.addItems(
            ["COM" + str(number) for number in range(MAX_COMBOBOX_ITEMS + 1)]
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
        # TODO: actually check the instrument connectivity in this widget

    def connect_widgets(self):
        """Give widgets logic."""
        # changing the oven combobox updates the oven port instantly
        self.oven_combobox.currentTextChanged.connect(
            lambda new_port: self.instruments.oven.update_port(new_port)
        )

    def update(self):
        """Update the state of dynamic widgets."""
        # update the oven label
        if self.instruments.oven.connected:
            text = "CONNECTED"
            color = "green"
        else:
            text = "DISCONNECTED"
            color = "red"
        self.oven_connection_label.setText(text)
        self.oven_connection_label.setStyleSheet("color: " + color)  # this is HTML syntax
