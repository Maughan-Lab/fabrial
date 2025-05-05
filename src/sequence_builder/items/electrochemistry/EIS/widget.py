from typing import Any, Self

from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QCheckBox, QFormLayout, QVBoxLayout

from .....classes.descriptions import DescriptionInfo
from .....custom_widgets.augmented.spin_box import DoubleSpinBox, SpinBox
from .....custom_widgets.container import Container
from .....gamry_integration.gamry import GAMRY
from .....utility.layouts import add_to_form_layout, clear_layout
from ...base_widget import AbstractBaseWidget
from . import encoding
from .process import EISProcess


class EISWidget(AbstractBaseWidget):
    """Contains entries for EIS experiments."""

    def __init__(self) -> None:
        """Create a new instance."""
        super().__init__(
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
                        "INITIAL_FREQUENCY": encoding.INITIAL_FREQUENCY,
                        "FINAL_FREQUENCY": encoding.FINAL_FREQUENCY,
                        "POINTS_PER_DECADE": encoding.POINTS_PER_DECADE,
                        "AC_VOLTAGE": encoding.AC_VOLTAGE,
                        "SAMPLE_AREA": encoding.AREA,
                        "ESTIMATED_IMPEDANCE": encoding.ESTIMATED_IMPEDANCE,
                    }
                ),
            ),
        )
        self.pstat_checkboxes: dict[str, QCheckBox] = {}
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
        self.area_spinbox = DoubleSpinBox(4)
        self.estimated_impedance_spinbox = DoubleSpinBox(4)

        add_to_form_layout(
            layout,
            (encoding.SELECTED_PSTATS, device_list_container),
            (encoding.DC_VOLTAGE, self.DC_voltage_spinbox),
            (encoding.INITIAL_FREQUENCY, self.initial_frequency_spinbox),
            (encoding.FINAL_FREQUENCY, self.final_frequency_spinbox),
            (encoding.POINTS_PER_DECADE, self.points_per_decade_spinbox),
            (encoding.AC_VOLTAGE, self.AC_voltage_spinbox),
            (encoding.AREA, self.area_spinbox),
            (encoding.ESTIMATED_IMPEDANCE, self.estimated_impedance_spinbox),
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
        super().showEvent(event)

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
        widget.area_spinbox.setValue(data_as_dict[encoding.AREA])
        widget.estimated_impedance_spinbox.setValue(data_as_dict[encoding.ESTIMATED_IMPEDANCE])
        widget.reload_pstat_list(data_as_dict[encoding.SELECTED_PSTATS])

        return widget

    def to_dict(self) -> dict:
        data = {
            encoding.DC_VOLTAGE: self.DC_voltage_spinbox.value(),
            encoding.INITIAL_FREQUENCY: self.initial_frequency_spinbox.value(),
            encoding.FINAL_FREQUENCY: self.final_frequency_spinbox.value(),
            encoding.POINTS_PER_DECADE: self.points_per_decade_spinbox.value(),
            encoding.AC_VOLTAGE: self.AC_voltage_spinbox.value(),
            encoding.AREA: self.area_spinbox.value(),
            encoding.ESTIMATED_IMPEDANCE: self.estimated_impedance_spinbox.value(),
            encoding.SELECTED_PSTATS: self.selected_pstats(),
        }
        return data
