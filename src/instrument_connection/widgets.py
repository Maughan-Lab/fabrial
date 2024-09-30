from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox, QWidget
from helper_widgets.label import Label  # ../helper_widgets
from instruments import InstrumentSet  # ../instruments.py


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

        # TODO: add a clock that calls update() every X seconds

    def create_widgets(self, layout: QHBoxLayout):
        """Create subwidgets."""
        self.oven_combobox = QComboBox()
        self.oven_connection_label = Label()

        inner_layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(inner_layout)

        label_layout = QHBoxLayout()
        label_container = QWidget()
        label_container.setLayout(label_layout)
        label_layout.addWidget(Label("Status:"))
        label_layout.addWidget(self.oven_connection_label)

        inner_layout.addWidget(Label("Oven Port"))
        inner_layout.addWidget(self.oven_combobox)
        inner_layout.addWidget(label_container)

        # TODO: finish setting up this widget

    def connect_widgets(self):
        """Give widgets logic."""
        self.button.pressed.connect(
            lambda: self.instruments.oven.change_setpoint(self.setpoint_spinbox.value())
        )

    def update(self):
        """Update the state of all contained widgets."""
        temperature = self.instruments.oven.read_temp()
        self.temperature_label.setText(str(temperature) if temperature is not None else "-----")
        setpoint = self.instruments.oven.get_setpoint()
        self.setpoint_label.setText(str(setpoint) if setpoint is not None else "-----")
