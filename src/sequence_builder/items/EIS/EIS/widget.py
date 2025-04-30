from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFormLayout, QCheckBox
from .....utility.layouts import add_sublayout, add_to_layout, add_to_form_layout, clear_layout
from .....custom_widgets.spin_box import SpinBox, DoubleSpinBox
from .....custom_widgets.button import Button
from .....custom_widgets.label import Label
from typing import Any, Self
from . import encoding
from ...base_widget import BaseWidget
from .process import EISProcess
from .....gamry_integration.Gamry import GAMRY


class EISWidget(BaseWidget):
    """Contains entries for EIS experiments."""

    def __init__(self) -> None:
        """Create a new instance."""
        # TODO: description
        super().__init__(
            QVBoxLayout(),
            "Electrochemical Impedance Spectroscopy",
            EISProcess,
            "battery-charge.png",
        )
        self.pstat_checkboxes: dict[str, QCheckBox] = {}
        self.create_widgets()

    def create_widgets(self) -> None:
        """Create subwidgets."""
        layout: QVBoxLayout = self.parameter_widget().layout()  # type: ignore

        button_layout = add_sublayout(layout, QHBoxLayout)
        self.reload_button = Button(
            "Reload Device List", lambda: self.reload_pstat_list(self.selected_pstats())
        )
        add_to_layout(button_layout, self.reload_button)

        device_list_layout = add_sublayout(layout, QHBoxLayout)
        device_list_layout.addWidget(Label("Potentiostat(s)"))
        self.devices_layout = add_sublayout(device_list_layout, QVBoxLayout)

        parameter_layout = add_sublayout(layout, QFormLayout)

        self.initial_frequency_spinbox = DoubleSpinBox(4)
        self.final_frequency_spinbox = DoubleSpinBox(4)
        self.points_per_decade_spinbox = SpinBox()
        self.AC_voltage_spinbox = DoubleSpinBox(4)
        self.DC_voltage_spinbox = DoubleSpinBox(4)
        self.area_spinbox = DoubleSpinBox(4)
        self.estimated_impedance_spinbox = DoubleSpinBox(4)

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

    def reload_pstat_list(self, selected_pstats: list[str]) -> None:
        """
        Reload the list of available potentiostats.

        :param selected_pstats: A list of potentiostat identifiers which should be checked.
        """
        identifiers: list[str] = GAMRY.get_pstat_list()
        clear_layout(self.devices_layout)
        self.pstat_checkboxes.clear()

        for identifier in identifiers:
            checkbox = QCheckBox(identifier)
            self.pstat_checkboxes.update({identifier: checkbox})
            if identifier in selected_pstats:
                checkbox.setChecked(True)
            self.devices_layout.addWidget(checkbox)

    def selected_pstats(self) -> list[str]:
        """Get a list of the selected potentiostats. The list contains pstat identifiers."""
        selected_pstats: list[str] = []
        for identifier, checkbox in self.pstat_checkboxes.items():
            if checkbox.isChecked():
                selected_pstats.append(identifier)
        return selected_pstats

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.initial_frequency_spinbox.setValue(data_as_dict[encoding.INITIAL_FREQUENCY])
        widget.final_frequency_spinbox.setValue(data_as_dict[encoding.FINAL_FREQUENCY])
        widget.points_per_decade_spinbox.setValue(data_as_dict[encoding.POINTS_PER_DECADE])
        widget.AC_voltage_spinbox.setValue(data_as_dict[encoding.AC_VOLTAGE])
        widget.DC_voltage_spinbox.setValue(data_as_dict[encoding.DC_voltage])
        widget.area_spinbox.setValue(data_as_dict[encoding.AREA])
        widget.estimated_impedance_spinbox.setValue(data_as_dict[encoding.ESTIMATED_IMPEDANCE])
        widget.reload_pstat_list(data_as_dict[encoding.SELECTED_PSTATS])
        return widget

    def to_dict(self) -> dict:
        data = {
            encoding.INITIAL_FREQUENCY: self.initial_frequency_spinbox.value(),
            encoding.FINAL_FREQUENCY: self.final_frequency_spinbox.value(),
            encoding.POINTS_PER_DECADE: self.points_per_decade_spinbox.value(),
            encoding.AC_VOLTAGE: self.AC_voltage_spinbox.value(),
            encoding.DC_voltage: self.DC_voltage_spinbox.value(),
            encoding.AREA: self.area_spinbox.value(),
            encoding.ESTIMATED_IMPEDANCE: self.estimated_impedance_spinbox.value(),
            encoding.SELECTED_PSTATS: self.selected_pstats(),
        }
        return data
