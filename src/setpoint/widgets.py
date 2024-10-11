from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.label import Label  # ../custom_widgets
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.new_timer import new_timer  # ../helper_functions


class SetpointWidget(QGroupBox):
    """
    Widget for changing the setpoint.

    :param instruments: Container for instruments.
    """

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Setpoint")  # set the frame's title
        # manage the layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.connect_widgets()
        self.update()

        self.update_timer = new_timer(0, self.update)  # timer to update the widgets

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

    def update(self):
        """Update the state of dynamic widgets."""
        # disable the setpoint button if the oven is disconnected or something else is using it
        self.button.setDisabled(
            False if self.instruments.oven.connected and self.instruments.oven.unlocked else True
        )
