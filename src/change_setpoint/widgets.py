from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QPushButton
from helper_widgets.spin_box import TemperatureSpinBox  # ../widgets
from temperature_sensor import Oven  # ../temperature_sensor.py


class SetTempWidget(QGroupBox):
    def __init__(self, oven: Oven):
        super().__init__()
        self.setTitle("Change setpoint")  # set the frame's title
        # manage the layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.setup_instruments(oven)
        self.create_widgets(layout)
        self.connect_widgets()

    def setup_instruments(self, *instruments: Oven):
        """Instantiate instruments."""
        self.oven = instruments[0]

    def create_widgets(self, layout: QVBoxLayout):
        """Create subwidgets."""
        layout.addWidget(QLabel("Setpoint"))

        self.setpoint_spinbox = TemperatureSpinBox()
        layout.addWidget(self.setpoint_spinbox)

        self.button = QPushButton("Change setpoint")
        layout.addWidget(self.button)

    def connect_widgets(self):
        """Give widgets logic."""
        self.button.pressed.connect(
            lambda: self.oven.change_setpoint(self.setpoint_spinbox.value())
        )
