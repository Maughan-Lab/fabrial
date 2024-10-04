from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QPushButton, QWidget
from PyQt6.QtCore import QTimer
from helper_widgets.spin_box import TemperatureSpinBox  # ../helper_widgets
from helper_widgets.label import Label  # ../helper_widgets
from instruments import InstrumentSet  # ../instruments.py


class StabilityCheckWidget(QGroupBox):
    """Widget for checking whether the temperature is stable."""

    def __init__(self, instruments: InstrumentSet):
        super().__init__()
        self.setTitle("Temperature Stability Check")

        # manage the layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.instruments = instruments
        self.create_widgets(layout)
        self.update()

        # timer to update the widgets
        update_timer = QTimer()  # default interval is 0 seconds, so as often as possible
        update_timer.timeout.connect(self.update)
        update_timer.start()

        self.setFixedSize(self.sizeHint())  # make sure expanding the window behaves correctly

    def create_widgets(self, layout: QVBoxLayout):
        """Create subwidgets."""
        self.stability_check_button = QPushButton()
        self.detect_setpoint_button = QPushButton()
        self.setpoint_spinbox = TemperatureSpinBox()

        # TODO: finish implementing this widget. You need a grid layout for the spinbox, label, and button
        # NOTE: the actual backend logic for this widget should be in another file.

    def connect_widgets(self):
        """Give widgets logic."""
        self.button.pressed.connect()  # TODO: connect this
        self.detect_setpoint_button.pressed.connect(self.detect_setpoint)

    def update(self):
        """Update the state of dynamic widgets."""
        # disable the button if the oven is disconnected
        self.button.setDisabled(True if self.instruments.oven.connected else False)

    def detect_setpoint(self):
        """Autofill the setpoint box with the oven's current setpoint."""
        setpoint = self.instruments.oven.get_setpoint()
        if setpoint is not None:
            self.setpoint_spinbox.setValue(setpoint)
        else:
            self.setpoint_spinbox.clear()  # clear the spinbox if the oven returns None
