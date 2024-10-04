from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QWidget
from PyQt6.QtCore import QTimer
from helper_widgets.label import Label  # ../helper_widgets
from helper_widgets.combo_box import ComboBox  # ../helper_widgets
from instruments import InstrumentSet  # ../instruments.py

MAX_COMBOBOX_ITEMS = 500


class InstrumentConnectionWidget(QGroupBox):
    """Widget for changing the instrument connection ports."""

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Instrument Connections")
        # manage the layout
        layout = QHBoxLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.connect_widgets()
        self.update()

        # timer to check the connection of the instruments every few seconds
        update_timer = QTimer()
        update_timer.setInterval(3000)  # 3 seconds
        update_timer.timeout.connect(self.update)
        update_timer.start()

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
        inner_layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(inner_layout)
        layout.addWidget(container)
        # the top label
        inner_layout.addWidget(Label("Oven Port"))
        # the combobox
        inner_layout.addWidget(self.oven_combobox)
        # the two bottom labels with the connection status
        label_layout = QHBoxLayout()
        label_container = QWidget()
        label_container.setLayout(label_layout)
        inner_layout.addWidget(label_container)
        label_layout.addWidget(Label("Status:"))
        label_layout.addWidget(self.oven_connection_label)

        # TODO: fix the spacing on the bottom label

        # NOTE: when adding additional instruments, make sure they can never use the same port

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
