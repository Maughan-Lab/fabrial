import json

from PyQt6.QtWidgets import QFormLayout

from ...constants import APP_NAME
from ...constants.paths.settings import oven as oven_settings
from ..augmented import DoubleSpinBox, SpinBox
from .settings_description import SettingsDescriptionWidget


class OvenSettingsTab(SettingsDescriptionWidget):
    """Oven settings."""

    MINIMUM_MEASUREMENT_INTERVAL = 50

    def __init__(self) -> None:
        try:
            with open(oven_settings.SAVED_SETTINGS_FILE, "r") as f:
                saved_settings = json.load(f)
        except Exception:
            with open(oven_settings.DEFAULT_SETTINGS_FILE, "r") as f:
                saved_settings = json.load(f)
        number_of_decimals = saved_settings[oven_settings.NUM_DECIMALS]

        layout = QFormLayout()
        SettingsDescriptionWidget.__init__(self, layout)
        self.set_description_from_file(
            oven_settings.DESCRIPTION_FOLDER,
            oven_settings.DESCRIPTION_FILENAME,
            {
                "APPLICATION_NAME": APP_NAME,
                "MINIMUM_TEMPERATURE": oven_settings.MIN_TEMPERATURE,
                "MAXIMUM_TEMPERATURE": oven_settings.MAX_TEMPERATURE,
                "MEASUREMENT_INTERVAL": oven_settings.MEASUREMENT_INTERVAL,
                "STABILITY_TOLERANCE": oven_settings.STABILITY_TOLERANCE,
                "MINIMUM_STABILITY_MEASUREMENTS": oven_settings.MINIMUM_STABILITY_MEASUREMENTS,
                "STABILITY_CHECK_INTERVAL": oven_settings.STABILITY_MEASUREMENT_INTERVAL,
                "TEMPERATURE_REGISTER": oven_settings.TEMPERATURE_REGISTER,
                "SETPOINT_REGISTER": oven_settings.SETPOINT_REGISTER,
                "NUMBER_OF_DECIMALS": oven_settings.NUM_DECIMALS,
            },
        )

        self.minimum_temperature_spinbox = DoubleSpinBox(
            number_of_decimals,
            -DoubleSpinBox.LARGEST_FLOAT,
            initial_value=saved_settings[oven_settings.MIN_TEMPERATURE],
        )
        self.maximum_temperature_spinbox = DoubleSpinBox(
            number_of_decimals,
            -DoubleSpinBox.LARGEST_FLOAT,
            initial_value=saved_settings[oven_settings.MAX_TEMPERATURE],
        )
        self.measurement_interval_spinbox = SpinBox(
            self.MINIMUM_MEASUREMENT_INTERVAL,
            initial_value=saved_settings[oven_settings.MEASUREMENT_INTERVAL],
        )
        self.stability_tolerance_spinbox = DoubleSpinBox(
            number_of_decimals, initial_value=saved_settings[oven_settings.STABILITY_TOLERANCE]
        )
        self.minimum_stability_measurements_spinbox = SpinBox(
            initial_value=saved_settings[oven_settings.MINIMUM_STABILITY_MEASUREMENTS]
        )
        self.stability_measurement_interval_spinbox = SpinBox(
            self.MINIMUM_MEASUREMENT_INTERVAL,
            initial_value=saved_settings[oven_settings.STABILITY_MEASUREMENT_INTERVAL],
        )
        self.temperature_register_spinbox = SpinBox(
            initial_value=saved_settings[oven_settings.TEMPERATURE_REGISTER]
        )
        self.setpoint_register_spinbox = SpinBox(
            initial_value=saved_settings[oven_settings.SETPOINT_REGISTER]
        )
        self.number_of_decimals_spinbox = SpinBox(
            initial_value=saved_settings[oven_settings.NUM_DECIMALS]
        )

        self.spinbox_dict: dict[str, SpinBox | DoubleSpinBox] = {
            oven_settings.MIN_TEMPERATURE: self.minimum_temperature_spinbox,
            oven_settings.MAX_TEMPERATURE: self.maximum_temperature_spinbox,
            oven_settings.MEASUREMENT_INTERVAL: self.measurement_interval_spinbox,
            oven_settings.STABILITY_TOLERANCE: self.stability_tolerance_spinbox,
            oven_settings.MINIMUM_STABILITY_MEASUREMENTS: (
                self.minimum_stability_measurements_spinbox
            ),
            oven_settings.STABILITY_MEASUREMENT_INTERVAL: (
                self.stability_measurement_interval_spinbox
            ),
            oven_settings.TEMPERATURE_REGISTER: self.temperature_register_spinbox,
            oven_settings.SETPOINT_REGISTER: self.setpoint_register_spinbox,
            oven_settings.NUM_DECIMALS: self.number_of_decimals_spinbox,
        }

        for name, spinbox in self.spinbox_dict.items():
            layout.addRow(name, spinbox)

        self.number_of_decimals_spinbox.valueChanged.connect(self.handle_decimal_change)

    def handle_decimal_change(self, decimal_count: int):
        """Handle the decimal number changing."""
        for spinbox in (
            self.maximum_temperature_spinbox,
            self.minimum_temperature_spinbox,
            self.stability_tolerance_spinbox,
        ):
            spinbox.setDecimals(decimal_count)

    def save_on_close(self):
        """Call this when closing the settings window to save settings."""
        settings_dict = {key: spinbox.value() for key, spinbox in self.spinbox_dict.items()}
        with open(oven_settings.SAVED_SETTINGS_FILE, "w") as f:
            json.dump(settings_dict, f)
