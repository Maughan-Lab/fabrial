from typing import Any, Self

from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QCheckBox, QFormLayout, QHBoxLayout, QRadioButton, QVBoxLayout

from .....classes import DescriptionInfo
from .....custom_widgets import Container, DoubleSpinBox, SpinBox
from .....gamry_integration import GAMRY
from .....utility import layout as layout_util
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import EISProcess


class EISWidget(AbstractBaseWidget):
    """Contains entries for EIS experiments."""

    def __init__(self) -> None:
        """Create a new instance."""
        AbstractBaseWidget.__init__(
            self,
            QFormLayout(),
            "Electrochemical Impedance Spectroscopy",
            EISProcess,
            "battery-charge.png",
            DescriptionInfo(
                "electrochemistry",
                "EIS",
                EISProcess.directory_name(),
                DescriptionInfo.Substitutions(
                    parameters_dict={
                        "POTENTIOSTATS": encoding.SELECTED_PSTATS,
                        "DC_VOLTAGE": encoding.DC_VOLTAGE,
                        "VS_EREF": encoding.VS_EREF,
                        "VS_EOC": encoding.VS_EOC,
                        "INITIAL_FREQUENCY": encoding.INITIAL_FREQUENCY,
                        "FINAL_FREQUENCY": encoding.FINAL_FREQUENCY,
                        "POINTS_PER_DECADE": encoding.POINTS_PER_DECADE,
                        "AC_VOLTAGE": encoding.AC_VOLTAGE,
                        "ESTIMATED_IMPEDANCE": encoding.ESTIMATED_IMPEDANCE,
                    }
                ),
            ),
        )
        self.pstat_checkboxes: dict[str, QCheckBox] = dict()
        self.impedance_reader_speed_radiobuttons: list[QRadioButton] = []
        self.voltage_reference_radiobuttons: list[QRadioButton] = []

        self.create_widgets()

    def create_widgets(self) -> None:
        """Create subwidgets."""
        layout: QFormLayout = self.parameter_widget().layout()  # type: ignore

        self.devices_layout = QVBoxLayout()
        device_list_container = Container(self.devices_layout)

        self.DC_voltage_spinbox = DoubleSpinBox(4)
        self.initial_frequency_spinbox = DoubleSpinBox(4)
        self.final_frequency_spinbox = DoubleSpinBox(4)
        self.points_per_decade_spinbox = SpinBox()
        self.AC_voltage_spinbox = DoubleSpinBox(4)
        self.estimated_impedance_spinbox = DoubleSpinBox(4)

        impedance_reader_speed_layout = QHBoxLayout()
        impedance_reader_speed_container = Container(impedance_reader_speed_layout)
        for label in encoding.IMPEDANCE_READER_SPEED_DICT.keys():
            radiobutton = QRadioButton(label)
            self.impedance_reader_speed_radiobuttons.append(radiobutton)
            impedance_reader_speed_layout.addWidget(radiobutton)

        dc_voltage_layout = QHBoxLayout()
        dc_voltage_layout.addWidget(self.DC_voltage_spinbox)
        voltage_reference_layout = QHBoxLayout()
        dc_voltage_layout.addLayout(voltage_reference_layout)
        dc_voltage_container = Container(dc_voltage_layout)
        for label in (encoding.VS_EREF, encoding.VS_EOC):
            radiobutton = QRadioButton(label)
            self.voltage_reference_radiobuttons.append(radiobutton)
            voltage_reference_layout.addWidget(radiobutton)

        layout_util.add_to_form_layout(
            layout,
            (encoding.SELECTED_PSTATS, device_list_container),
            (encoding.DC_VOLTAGE, dc_voltage_container),
            (encoding.INITIAL_FREQUENCY, self.initial_frequency_spinbox),
            (encoding.FINAL_FREQUENCY, self.final_frequency_spinbox),
            (encoding.POINTS_PER_DECADE, self.points_per_decade_spinbox),
            (encoding.AC_VOLTAGE, self.AC_voltage_spinbox),
            (encoding.ESTIMATED_IMPEDANCE, self.estimated_impedance_spinbox),
            ("Optimize for", impedance_reader_speed_container),
        )

    def reload_pstat_list(self, selected_pstats: list[str]) -> None:
        """
        Reload the list of available potentiostats.

        Parameters
        ----------
        selected_pstats
            A list of potentiostat identifiers which should be checked.
        """
        identifiers: list[str] = GAMRY.get_pstat_list()
        layout_util.clear_layout(self.devices_layout)
        self.pstat_checkboxes.clear()

        for identifier in identifiers:
            checkbox = QCheckBox(identifier)
            self.pstat_checkboxes.update({identifier: checkbox})
            if identifier in selected_pstats:
                checkbox.setChecked(True)
            self.devices_layout.addWidget(checkbox)

    def selected_pstats(self) -> list[str]:
        """Get a list of the selected potentiostats. The list contains potentiostat identifiers."""
        selected_pstats: list[str] = []
        for identifier, checkbox in self.pstat_checkboxes.items():
            if checkbox.isChecked():
                selected_pstats.append(identifier)
        return selected_pstats

    def showEvent(self, event: QShowEvent | None):  # overridden
        if event is not None:
            # reload the device list when the window gets opened
            self.reload_pstat_list(self.selected_pstats())
        AbstractBaseWidget.showEvent(self, event)

    @staticmethod
    def allowed_to_create() -> bool:  # overridden
        return GAMRY.is_valid()

    @classmethod
    def from_dict(cls: type[Self], data_as_dict: dict[str, Any]) -> Self:
        widget = cls()
        widget.DC_voltage_spinbox.setValue(data_as_dict[encoding.DC_VOLTAGE])
        widget.initial_frequency_spinbox.setValue(data_as_dict[encoding.INITIAL_FREQUENCY])
        widget.final_frequency_spinbox.setValue(data_as_dict[encoding.FINAL_FREQUENCY])
        widget.points_per_decade_spinbox.setValue(data_as_dict[encoding.POINTS_PER_DECADE])
        widget.AC_voltage_spinbox.setValue(data_as_dict[encoding.AC_VOLTAGE])
        widget.estimated_impedance_spinbox.setValue(data_as_dict[encoding.ESTIMATED_IMPEDANCE])

        selected_speed_option = data_as_dict[encoding.IMPEDANCE_READER_SPEED]
        for radiobutton in widget.impedance_reader_speed_radiobuttons:
            if radiobutton.text() == selected_speed_option:
                radiobutton.setChecked(True)
                break

        selected_voltage_reference = data_as_dict[encoding.DC_VOLTAGE_REFERENCE]
        for radiobutton in widget.voltage_reference_radiobuttons:
            if radiobutton.text() == selected_voltage_reference:
                radiobutton.setChecked(True)
                break

        widget.reload_pstat_list(data_as_dict[encoding.SELECTED_PSTATS])

        return widget

    def to_dict(self) -> dict:
        for radiobutton in self.impedance_reader_speed_radiobuttons:
            if radiobutton.isChecked():
                selected_speed_option = radiobutton.text()
                break

        for radiobutton in self.voltage_reference_radiobuttons:
            if radiobutton.isChecked():
                selected_voltage_reference = radiobutton.text()
                break

        data = {
            encoding.DC_VOLTAGE: self.DC_voltage_spinbox.value(),
            encoding.DC_VOLTAGE_REFERENCE: selected_voltage_reference,
            encoding.INITIAL_FREQUENCY: self.initial_frequency_spinbox.value(),
            encoding.FINAL_FREQUENCY: self.final_frequency_spinbox.value(),
            encoding.POINTS_PER_DECADE: self.points_per_decade_spinbox.value(),
            encoding.AC_VOLTAGE: self.AC_voltage_spinbox.value(),
            encoding.ESTIMATED_IMPEDANCE: self.estimated_impedance_spinbox.value(),
            encoding.IMPEDANCE_READER_SPEED: selected_speed_option,
            encoding.SELECTED_PSTATS: self.selected_pstats(),
        }
        return data
