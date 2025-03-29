from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QCheckBox
from ...utility.layouts import (
    add_sublayout,
    add_sublayout_to_grid,
    add_to_layout,
    add_to_layout_grid,
    row_pair,
    clear_layout,
)
from ...custom_widgets.spin_box import SpinBox, DoubleSpinBox
from ...custom_widgets.button import Button
from ...custom_widgets.label import Label
from typing import Self
from ..data_encodings import EIS as DATA
from ..data_encodings.display_name import DISPLAY_NAME
from .base import BaseWidget

from ...gamry_integration.GamryCOM import GamryCOM
import comtypes.client as client


class EISWidget(BaseWidget):
    """Contains entries for EIS experiments."""

    def __init__(self):
        """Create a new instance."""
        super().__init__(QVBoxLayout)
        self.devices_list = []
        self.create_widgets()

    def create_widgets(self):
        """Create subwidgets."""
        # TODO: use a table instead of a bunch of spin boxes

        layout = self.layout()

        button_layout = add_sublayout(layout, QHBoxLayout)
        add_to_layout(
            button_layout,
            Button("Default", self.restore_defaults),
            Button("Reload Device List", self.reload_device_list),
        )

        parameter_layout = add_sublayout(layout, QGridLayout)

        parameter_layout.addWidget(Label("Potentiostat(s)"), 0, 0)
        self.devices_layout = add_sublayout_to_grid(parameter_layout, QVBoxLayout, 0, 1)
        self.reload_device_list()

        self.initial_frequency_spinbox = DoubleSpinBox()
        self.final_frequency_spinbox = DoubleSpinBox()
        self.points_per_decade_spinbox = SpinBox()
        self.AC_voltage_spinbox = DoubleSpinBox()
        self.DC_voltage_spinbox = DoubleSpinBox()
        self.area_spinbox = DoubleSpinBox()
        self.estimated_impedance_spinbox = DoubleSpinBox()

        add_to_layout_grid(
            parameter_layout,
            *row_pair(Label("Initial Freq. (Hz)"), self.initial_frequency_spinbox, 1),
            *row_pair(Label("Final Freq. (Hz)"), self.final_frequency_spinbox, 2),
            *row_pair(Label("Points/decade"), self.points_per_decade_spinbox, 3),
            *row_pair(Label("AC Voltage (mV rms)"), self.AC_voltage_spinbox, 4),
            *row_pair(Label("DC Voltage (V)"), self.DC_voltage_spinbox, 5),
            *row_pair(Label("Area (cm^2)"), self.area_spinbox, 6),
            *row_pair(Label("Estimated Z (ohms)"), self.estimated_impedance_spinbox, 7),
        )

    def reload_device_list(self):
        """Reload the list of available devices."""
        # get the device list from GamryCOM
        # clear the widgets in self.devices_layout
        # remake the widgets with the available list of devices
        # TODO: figure out if this is fast or slow
        clear_layout(self.devices_layout)
        devices = client.CreateObject(GamryCOM.GamryDeviceList)
        names = devices.EnumSections()
        for name in names:
            self.devices_layout.addWidget(QCheckBox(name))

    def restore_defaults(self):
        """Set all values to their default value."""
        # TODO: implement this or delete it if you don't need it
        pass

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict) -> Self:
        widget = cls()
        widget.set_display_name(data_as_dict[DISPLAY_NAME])
        widget.initial_frequency_spinbox.setValue(data_as_dict[DATA.INITIAL_FREQUENCY])
        widget.final_frequency_spinbox.setValue(data_as_dict[DATA.FINAL_FREQUENCY])
        widget.points_per_decade_spinbox.setValue(data_as_dict[DATA.POINTS_PER_DECADE])
        widget.AC_voltage_spinbox.setValue(data_as_dict[DATA.AC_VOLTAGE])
        widget.DC_voltage_spinbox.setValue(data_as_dict[DATA.DC_voltage])
        widget.area_spinbox.setValue(data_as_dict[DATA.AREA])
        widget.estimated_impedance_spinbox.setValue(data_as_dict[DATA.ESTIMATED_IMPEDANCE])
        return widget

    def to_dict(self) -> dict:
        data = {
            DISPLAY_NAME: self.display_name,
            DATA.INITIAL_FREQUENCY: self.initial_frequency_spinbox.value(),
            DATA.FINAL_FREQUENCY: self.final_frequency_spinbox.value(),
            DATA.POINTS_PER_DECADE: self.points_per_decade_spinbox.value(),
            DATA.AC_VOLTAGE: self.AC_voltage_spinbox.value(),
            DATA.DC_voltage: self.DC_voltage_spinbox.value(),
            DATA.AREA: self.area_spinbox.value(),
            DATA.ESTIMATED_IMPEDANCE: self.estimated_impedance_spinbox.value(),
        }
        return data
