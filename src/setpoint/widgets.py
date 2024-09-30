from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton
from helper_widgets.spin_box import TemperatureSpinBox  # ../helper_widgets
from helper_widgets.label import Label  # ../helper_widgets
from instruments import InstrumentSet  # ../instruments.py


class SetpointWidget(QGroupBox):
    """Widget for changing the setpoint."""

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Change Setpoint")  # set the frame's title
        # manage the layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.connect_widgets()

        self.setFixedSize(self.sizeHint())  # make sure expanding the window behaves correctly

    def create_widgets(self, layout: QVBoxLayout):
        """Create subwidgets."""
        layout.addWidget(Label("Setpoint"))

        self.setpoint_spinbox = TemperatureSpinBox()
        layout.addWidget(self.setpoint_spinbox)

        self.button = QPushButton("Change Setpoint")
        layout.addWidget(self.button)

    def connect_widgets(self):
        """Give widgets logic."""
        self.button.pressed.connect(
            lambda: self.instruments.oven.change_setpoint(self.setpoint_spinbox.value())
        )
