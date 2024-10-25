from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QSizePolicy
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.label import FixedLabel  # ../custom_widgets
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.new_timer import new_timer  # ../helper_functions
from helper_functions.layouts import add_to_layout


class SetpointWidget(QGroupBox):
    """
    Widget for changing the setpoint.

    :param instruments: Container for instruments.
    """

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Setpoint")  # set the frame's title
        # manage the layout
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.connect_widgets()

        self.update_timer = new_timer(0, self.update)  # timer to update the widgets

        self.update()

    def create_widgets(self, layout: QVBoxLayout):
        """Create subwidgets."""
        self.setpoint_spinbox = TemperatureSpinBox()
        self.button = QPushButton("Change Setpoint")
        add_to_layout(layout, FixedLabel("Setpoint"), self.setpoint_spinbox, self.button)

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
