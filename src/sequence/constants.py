import file_locations  # ../file_locations.py
from os import path

# sequence parameters
CYCLE_COLUMN = "Cycle"  # 0
TEMPERATURE_COLUMN = "Temp"  # 1
BUFFER_HOURS_COLUMN = "Buffer\nHours"  # 2
BUFFER_MINUTES_COLUMN = "Buffer\nMinutes"  # 3
HOLD_HOURS_COLUMN = "Hold\nHours"  # 4
HOLD_MINUTES_COLUMN = "Hold\nMinutes"  # 5

# files
SAVED_SETTINGS_FILE = path.join(file_locations.SAVED_SETTINGS_LOCATION + "sequence_settings.csv")

DATA_FILES_LOCATION = "Data Files"
PRE_STABLE_FILE = "Pre-Stabilization Temperature Data.csv"
BUFFER_FILE = "Buffer Temperature Data.csv"
STABLE_FILE = "Post-Stabilization Temperature Data.csv"
CYCLE_TIMES_FILE = "Cycle Times.csv"
STABILIZATON_TIMES_FILE = "Stabilization Times.csv"
GRAPH_FILE = "Sequence Graph.jpeg"

# format
DATE_FORMAT = "Day Month Year Hours:Minutes:Seconds AM/PM"

# for use by external modules
TIME = "Time (seconds)"
TEMPERATURE = "Oven Temperature (degrees C)"
