import json

from PyQt6.QtWidgets import QFormLayout

from ...Files import APPLICATION_NAME, Settings
from ..augmented.spin_box import DoubleSpinBox, SpinBox
from .settings_description import SettingsDescriptionWidget

SettingNames = Settings.Oven


class OvenSettingsTab(SettingsDescriptionWidget):
    """Oven settings."""

    MINIMUM_MEASUREMENT_INTERVAL = 50

    def __init__(self) -> None:
        try:
            with open(Settings.Oven.SAVED_SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        except Exception:
            with open(Settings.Oven.DEFAULT_SETTINGS_FILE, "r") as f:
                settings = json.load(f)
        number_of_decimals = settings[SettingNames.NUM_DECIMALS]

        layout = QFormLayout()
        super().__init__(layout)
        self.set_description_from_file(
            Settings.Oven.DESCRIPTION_FOLDER,
            Settings.Oven.DESCRIPTION_FILENAME,
            {
                "APPLICATION_NAME": APPLICATION_NAME,
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

        self.minimum_temperature_spinbox = DoubleSpinBox(
            number_of_decimals,
            -DoubleSpinBox.LARGEST_FLOAT,
            initial_value=settings[SettingNames.MIN_TEMPERATURE],
        )
        self.maximum_temperature_spinbox = DoubleSpinBox(
            number_of_decimals,
            -DoubleSpinBox.LARGEST_FLOAT,
            initial_value=settings[SettingNames.MAX_TEMPERATURE],
        )
        self.measurement_interval_spinbox = SpinBox(
            self.MINIMUM_MEASUREMENT_INTERVAL,
            initial_value=settings[SettingNames.MEASUREMENT_INTERVAL],
        )
        self.stability_tolerance_spinbox = DoubleSpinBox(
            number_of_decimals, initial_value=settings[SettingNames.STABILITY_TOLERANCE]
        )
        self.minimum_stability_measurements_spinbox = SpinBox(
            initial_value=settings[SettingNames.MINIMUM_STABILITY_MEASUREMENTS]
        )
        self.stability_measurement_interval_spinbox = SpinBox(
            self.MINIMUM_MEASUREMENT_INTERVAL,
            initial_value=settings[SettingNames.STABILITY_MEASUREMENT_INTERVAL],
        )
        self.temperature_register_spinbox = SpinBox(
            initial_value=settings[SettingNames.TEMPERATURE_REGISTER]
        )
        self.setpoint_register_spinbox = SpinBox(
            initial_value=settings[SettingNames.SETPOINT_REGISTER]
        )
        self.number_of_decimals_spinbox = SpinBox(initial_value=settings[SettingNames.NUM_DECIMALS])

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
        with open(Settings.Oven.SAVED_SETTINGS_FILE, "w") as f:
            json.dump(settings_dict, f)
