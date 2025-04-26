from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QCheckBox
from .....utility.layouts import add_sublayout, add_to_layout, add_to_form_layout, clear_layout
from .....custom_widgets.spin_box import SpinBox, DoubleSpinBox
from .....custom_widgets.button import Button
from .....custom_widgets.label import Label
from typing import Self
from . import encoding as DATA
from ...base_widget import BaseWidget
from .process import EISProcess

from .....gamry_integration.GamryCOM import GamryCOM
import comtypes.client as client  # type: ignore


class EISWidget(BaseWidget):
    """Contains entries for EIS experiments."""

    PROCESS_TYPE = EISProcess
    ICON = "battery-charge.png"

    def __init__(self):
        """Create a new instance."""
        super().__init__(QVBoxLayout(), "Electrochemical Impedance Spectroscopy")
        self.devices_list: list[str] = []
        self.create_widgets()

    def create_widgets(self) -> None:
        """Create subwidgets."""
        layout: QVBoxLayout = self.parameter_widget().layout()  # type: ignore

        button_layout = add_sublayout(layout, QHBoxLayout)
        add_to_layout(
            button_layout,
            Button("Default", self.restore_defaults),
            Button("Reload Device List", self.reload_device_list),
        )

        device_list_layout = add_sublayout(layout, QHBoxLayout)
        device_list_layout.addWidget(Label("Potentiostat(s)"))
        self.devices_layout = add_sublayout(device_list_layout, QVBoxLayout)
        self.reload_device_list()

        parameter_layout = add_sublayout(layout, QFormLayout)

        self.initial_frequency_spinbox = DoubleSpinBox()
        self.final_frequency_spinbox = DoubleSpinBox()
        self.points_per_decade_spinbox = SpinBox()
        self.AC_voltage_spinbox = DoubleSpinBox()
        self.DC_voltage_spinbox = DoubleSpinBox()
        self.area_spinbox = DoubleSpinBox()
        self.estimated_impedance_spinbox = DoubleSpinBox()

        add_to_form_layout(
            parameter_layout,
            ("Initial Freq. (Hz)", self.initial_frequency_spinbox),
            ("Final Freq. (Hz)", self.final_frequency_spinbox),
            ("Points/decade", self.points_per_decade_spinbox),
            ("AC Voltage (mV rms)", self.AC_voltage_spinbox),
            ("DC Voltage (V)", self.DC_voltage_spinbox),
            ("Area (cm^2)", self.area_spinbox),
            ("Estimated Z (ohms)", self.estimated_impedance_spinbox),
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
            DATA.INITIAL_FREQUENCY: self.initial_frequency_spinbox.value(),
            DATA.FINAL_FREQUENCY: self.final_frequency_spinbox.value(),
            DATA.POINTS_PER_DECADE: self.points_per_decade_spinbox.value(),
            DATA.AC_VOLTAGE: self.AC_voltage_spinbox.value(),
            DATA.DC_voltage: self.DC_voltage_spinbox.value(),
            DATA.AREA: self.area_spinbox.value(),
            DATA.ESTIMATED_IMPEDANCE: self.estimated_impedance_spinbox.value(),
        }
        return data
