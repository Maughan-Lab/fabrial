from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout
from custom_widgets.label import Label, FixedLabel  # ../custom_widgets
from custom_widgets.combo_box import ComboBox  # ../custom_widgets
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.add_sublayout import add_sublayout  # ../helper_functions
from helper_functions.new_timer import new_timer  # ../helper_functions

MAX_COMBOBOX_ITEMS = 500


class InstrumentConnectionWidget(QGroupBox):
    """
    Widget for changing the instrument connection ports.

    :param instruments: Container for instruments.
    """

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Instrument Connections")
        # manage the layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.connect_widgets()

        # timer to check the connection of the instruments every few seconds
        self.update_timer = new_timer(3000, self.update)

        self.update()
        self.setFixedSize(self.sizeHint())  # make sure expanding the window behaves correctly

    def create_widgets(self, layout: QHBoxLayout):
        """Create subwidgets."""
        self.oven_combobox = ComboBox()
        # add "COM1" through "COM500" to the combobox
        self.oven_combobox.addItems(
            ["COM" + str(number) for number in range(MAX_COMBOBOX_ITEMS + 1)]
        )
        self.oven_connection_label = Label()

        # this could probably be put in a for loop if more instruments are added
        inner_layout: QVBoxLayout = add_sublayout(layout, QVBoxLayout)
        inner_layout.addWidget(FixedLabel("Oven Port"))  # the top label
        inner_layout.addWidget(self.oven_combobox)  # the combobox
        # the two bottom labels with the connection status
        label_layout: QHBoxLayout = add_sublayout(inner_layout, QHBoxLayout)
        label_layout.addWidget(FixedLabel("Status:"))
        label_layout.addWidget(self.oven_connection_label)

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
        if self.instruments.oven.connected:
            self.oven_connection_label.setText("CONNECTED")
            self.oven_connection_label.setStyleSheet("color: green")  # this is HTML syntax
        else:
            self.oven_connection_label.setText("DISCONNECTED")
            self.oven_connection_label.setStyleSheet("color: red")
