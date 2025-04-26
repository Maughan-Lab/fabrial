from dataclasses import dataclass
import json
from .. import Files

TEMPERATURE_REGISTER = "temperature-register"
SETPOINT_REGISTER = "setpoint_register"
MAX_TEMPERATURE = "max-temperature"
MIN_TEMPERATURE = "min-temperature"
NUM_DECIMALS = "number-of-decimals"


@dataclass
class OvenSettings:
    TEMPERATURE_REGISTER: int
    SETPOINT_REGISTER: int
    MAX_TEMPERATURE: float
    MIN_TEMPERATURE: float
    NUM_DECIMALS: int


def get_oven_settings() -> OvenSettings:
    """Get the oven's settings from the oven settings file."""
    with open(Files.Oven.SETTINGS_FILE, "r") as f:
        settings = json.load(f)
    return OvenSettings(
        settings[TEMPERATURE_REGISTER],
        settings[SETPOINT_REGISTER],
        settings[MAX_TEMPERATURE],
        settings[MIN_TEMPERATURE],
        settings[NUM_DECIMALS],
    )


def write_oven_settings(settings: OvenSettings):
    """Write the oven settings to the oven settings file."""
    settings_dict = {
        TEMPERATURE_REGISTER: settings.TEMPERATURE_REGISTER,
        SETPOINT_REGISTER: settings.SETPOINT_REGISTER,
        MAX_TEMPERATURE: settings.MAX_TEMPERATURE,
        MIN_TEMPERATURE: settings.MIN_TEMPERATURE,
        NUM_DECIMALS: settings.NUM_DECIMALS,
    }
    with open(Files.Oven.SETTINGS_FILE, "w") as f:
        json.dump(settings_dict, f)
