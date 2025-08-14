"""Filepaths and dictionary keys for oven settings."""

from .defaults import DEFAULT_SETTINGS
from .saved import SAVED_SETTINGS

SETTINGS_FOLDER_NAME = "oven"
SETTINGS_FILENAME = "oven_settings.json"

# files
SAVED_SETTINGS_FOLDER = SAVED_SETTINGS.joinpath(SETTINGS_FOLDER_NAME)
SAVED_SETTINGS_FILE = SAVED_SETTINGS.joinpath(SETTINGS_FILENAME)
DEFAULT_SETTINGS_FILE = DEFAULT_SETTINGS.joinpath(SETTINGS_FOLDER_NAME, SETTINGS_FILENAME)
OVEN_PORT_FILE = SAVED_SETTINGS.joinpath("oven_port.csv")
DESCRIPTION_FOLDER = DEFAULT_SETTINGS.joinpath(SETTINGS_FOLDER_NAME)
DESCRIPTION_FILENAME = "description.md"
# keys
TEMPERATURE_REGISTER = "Temperature Register"
SETPOINT_REGISTER = "Setpoint Register"
MAX_TEMPERATURE = "Maximum Temperature"
MIN_TEMPERATURE = "Minimum Temperature"
NUM_DECIMALS = "Number of Decimals"
STABILITY_TOLERANCE = "Stability Tolerance"
MEASUREMENT_INTERVAL = "Measurement Interval (ms)"
MINIMUM_STABILITY_MEASUREMENTS = "Minimum Measurements for Stability"
STABILITY_MEASUREMENT_INTERVAL = "Stability Check Interval (ms)"
