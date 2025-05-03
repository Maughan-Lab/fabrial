import json
from typing import Self

from PyQt6.QtWidgets import QFormLayout

from ... import Files
from ..augmented.spin_box import DoubleSpinBox, SpinBox
from .settings_description import SettingsDescriptionWidget

SettingNames = Files.ApplicationSettings.Oven


class OvenSettingsTab(SettingsDescriptionWidget):
    """Oven settings."""

    MINIMUM_MEASUREMENT_INTERVAL = 50

    def __init__(self) -> None:
        layout = QFormLayout()
        super().__init__(layout)
        Filenames = Files.ApplicationSettings.Oven
        self.set_description_from_file(
            Filenames.FOLDER,
            Filenames.DESCRIPTION_FILENAME,
            {
                "APPLICATION_NAME": Files.APPLICATION_NAME,
                "MINIMUM_TEMPERATURE": SettingNames.MIN_TEMPERATURE,
                "MAXIMUM_TEMPERATURE": SettingNames.MAX_TEMPERATURE,
                "MEASUREMENT_INTERVAL": SettingNames.MEASUREMENT_INTERVAL,
                "STABILITY_TOLERANCE": SettingNames.STABILITY_TOLERANCE,
                "MINIMUM_STABILITY_MEASUREMENTS": SettingNames.MINIMUM_STABILITY_MEASUREMENTS,
                "STABILITY_CHECK_INTERVAL": SettingNames.STABILITY_MEASUREMENT_INTERVAL,
                "TEMPERATURE_REGISTER": SettingNames.TEMPERATURE_REGISTER,
                "SETPOINT_REGISTER": SettingNames.SETPOINT_REGISTER,
                "NUMBER_OF_DECIMALS": SettingNames.NUM_DECIMALS,
            },
        )

        self.minimum_temperature_spinbox = DoubleSpinBox(minimum=-DoubleSpinBox.LARGEST_FLOAT)
        self.maximum_temperature_spinbox = DoubleSpinBox(minimum=-DoubleSpinBox.LARGEST_FLOAT)
        self.measurement_interval_spinbox = SpinBox(self.MINIMUM_MEASUREMENT_INTERVAL)
        self.stability_tolerance_spinbox = DoubleSpinBox()
        self.minimum_stability_measurements_spinbox = SpinBox()
        self.stability_measurement_interval_spinbox = SpinBox(self.MINIMUM_MEASUREMENT_INTERVAL)
        self.temperature_register_spinbox = SpinBox()
        self.setpoint_register_spinbox = SpinBox()
        self.number_of_decimals_spinbox = SpinBox()

        self.spinbox_dict: dict[str, SpinBox | DoubleSpinBox] = {
            SettingNames.MIN_TEMPERATURE: self.minimum_temperature_spinbox,
            SettingNames.MAX_TEMPERATURE: self.maximum_temperature_spinbox,
            SettingNames.MEASUREMENT_INTERVAL: self.measurement_interval_spinbox,
            SettingNames.STABILITY_TOLERANCE: self.stability_tolerance_spinbox,
            SettingNames.MINIMUM_STABILITY_MEASUREMENTS: self.minimum_stability_measurements_spinbox,
            SettingNames.STABILITY_MEASUREMENT_INTERVAL: self.stability_measurement_interval_spinbox,
            SettingNames.TEMPERATURE_REGISTER: self.temperature_register_spinbox,
            SettingNames.SETPOINT_REGISTER: self.setpoint_register_spinbox,
            SettingNames.NUM_DECIMALS: self.number_of_decimals_spinbox,
        }

        for name, spinbox in self.spinbox_dict.items():
            layout.addRow(name, spinbox)

    def reinitialize(self) -> Self:
        """Initialize the settings from the oven settings file."""
        with open(Files.ApplicationSettings.Oven.SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        number_of_decimals = settings[SettingNames.NUM_DECIMALS]

        spinbox: SpinBox | DoubleSpinBox

        for spinbox in (
            self.minimum_temperature_spinbox,
            self.maximum_temperature_spinbox,
            self.stability_tolerance_spinbox,
        ):
            spinbox.setDecimals(number_of_decimals)

        for key, spinbox in self.spinbox_dict.items():
            spinbox.setValue(settings[key])

        return self

    def save_on_close(self):
        """Call this when closing the settings window to save settings."""
        settings_dict = {key: spinbox.value() for key, spinbox in self.spinbox_dict.items()}
        with open(Files.ApplicationSettings.Oven.SETTINGS_FILE, "w") as f:
            json.dump(settings_dict, f)
