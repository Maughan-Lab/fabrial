from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.label import Label  # ../custom_widgets
from instruments import InstrumentSet  # ../instruments.py
from helper_functions.add_sublayout import add_sublayout  # ../helper_functions
from helper_functions.new_timer import new_timer  # ../helper_functions
from .stability_check import test


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
        self.connect_widgets()
        self.update()

        self.update_timer = new_timer(0, self.update)  # timer to update the widgets

        self.setFixedSize(self.sizeHint())  # make sure expanding the window behaves correctly

    def create_widgets(self, layout: QVBoxLayout):
        """Create subwidgets."""
        self.stability_check_button = QPushButton("Check Stability")
        self.detect_setpoint_button = QPushButton("Detect Setpoint")
        self.setpoint_spinbox = TemperatureSpinBox()
        self.stability_status_label = Label("--------")

        # layout for the label, detect_setpoint_button, and setpoint_spinbox
        inner_layout: QGridLayout = add_sublayout(layout, QGridLayout)
        inner_layout.addWidget(Label("Setpoint"), 0, 0)
        inner_layout.addWidget(self.setpoint_spinbox, 1, 0)
        inner_layout.addWidget(self.detect_setpoint_button, 1, 1)

        layout.addWidget(self.stability_check_button)  # add the button that checks oven stability
        # layout for the labels at the bottom
        label_layout: QHBoxLayout = add_sublayout(layout, QHBoxLayout)
        label_layout.addWidget(Label("Oven Status:"))
        label_layout.addWidget(self.stability_status_label)

        # NOTE: the actual backend logic for this widget should be in another file.
        # TODO: fix the spacing for the nested layouts

    def connect_widgets(self):
        """Give widgets logic."""
        # self.stability_check_button.pressed.connect()  # TODO: connect this
        self.detect_setpoint_button.pressed.connect(self.detect_setpoint)

    def update(self):
        """Update the state of dynamic widgets."""
        # disable the buttons if the oven is disconnected
        for button in (self.detect_setpoint_button, self.stability_check_button):
            button.setDisabled(True if not self.instruments.oven.connected else False)

    def detect_setpoint(self):
        """Autofill the setpoint box with the oven's current setpoint."""
        setpoint = self.instruments.oven.get_setpoint()
        if setpoint is not None:
            self.setpoint_spinbox.setValue(setpoint)
        else:
            self.setpoint_spinbox.clear()  # clear the spinbox if the oven is disconnected

    def test(self):
        test(self)
