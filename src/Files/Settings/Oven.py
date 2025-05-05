"""Filepaths and dictionary keys for oven settings."""

import os

from . import saved
from .defaults import DEFAULT_SETTINGS_FOLDER

SETTINGS_FOLDER_NAME = "oven"
SETTINGS_FILENAME = "oven_settings.json"

# files
SAVED_SETTINGS_FOLDER = os.path.join(saved.SAVED_SETTINGS_FOLDER, SETTINGS_FOLDER_NAME)
SAVED_SETTINGS_FILE = os.path.join(SAVED_SETTINGS_FOLDER, SETTINGS_FILENAME)
DEFAULT_SETTINGS_FILE = os.path.join(
    DEFAULT_SETTINGS_FOLDER, SETTINGS_FOLDER_NAME, SETTINGS_FILENAME
)
OVEN_PORT_FILE = os.path.join(SAVED_SETTINGS_FOLDER, "oven_port.csv")
DESCRIPTION_FOLDER = os.path.join(DEFAULT_SETTINGS_FOLDER, SETTINGS_FOLDER_NAME)
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
