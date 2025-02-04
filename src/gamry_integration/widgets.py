from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton
from PyQt6.QtCore import pyqtSignal
from utility.layouts import (
    add_sublayout,
    add_sublayout_to_grid,
    add_to_layout,
    add_to_layout_grid,
    row_pair,
)
from custom_widgets.spin_box import SpinBox, DoubleSpinBox
from custom_widgets.container import Container
from custom_widgets.button import Button
from custom_widgets.label import Label


class EISOptionsWidget(Container):
    def __init__(self):
        super().__init__(QVBoxLayout)
        self.devices_list = []
        self.create_widgets()
        self.connect_widgets()
        self.connect_signals()

    def create_widgets(self):
        """Create subwidgets."""
        layout = self.layout()

        button_layout = add_sublayout(layout, QHBoxLayout)
        add_to_layout(
            button_layout,
            Button("Default", self.restore_defaults),
            Button("Reload Device List", self.reload_device_list),
        )

        parameter_layout = add_sublayout(layout, QGridLayout)

        parameter_layout.addWidget(Label("Potentiostat(s)"), 0, 0)
        self.devices_layout = add_sublayout_to_grid(layout, QVBoxLayout, 0, 1)
        self.reload_device_list()

        self.initial_frequency_spinbox = DoubleSpinBox()
        self.final_frequency_spinbox = DoubleSpinBox()
        self.points_per_decade_spinbox = SpinBox()
        self.AC_voltage_spinbox = DoubleSpinBox()
        self.DC_voltage_spinbox = DoubleSpinBox()
        self.area_spinbox = DoubleSpinBox()
        self.estimated_impedance_spinbox = DoubleSpinBox()

        # TODO: finish adding to the layout

        add_to_layout_grid(
            layout,
            *row_pair(Label("Initial Freq. (Hz)"), self.initial_frequency_spinbox, 1),
            *row_pair(Label("Final Freq. (Hz)"), self.final_frequency_spinbox, 2),
            *row_pair(Label("Points/decade"), self.points_per_decade_spinbox, 3),
            *row_pair(Label("AC Voltage (mV rms)"), self.AC_voltage_spinbox, 4),
            *row_pair(Label("DC Voltage (V)"), self.DC_voltage_spinbox, 5),
            # still need area and estimated impedance
        )

    def reload_device_list(self):
        """Reload the list of available devices."""
        # get the device list from GamryCOM
        # clear the widgets in self.devices_layout
        # remake the widgets with the available list of devices
        pass

    def restore_defaults(self):
        """Set all values to their default value."""
        pass

    def to_dict(self) -> dict:
        # TODO: implement this
        return {}
