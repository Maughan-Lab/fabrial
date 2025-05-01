"""File and folder locations for the whole application."""

import os

SAVED_SETTINGS_FOLDER = "saved_settings"
APPLICATION_NAME = "Quincy"


class Icons:
    """Icon file/folder names."""

    MAIN_ICON = "icons/oven_icon.png"
    INTERNAL_ICONS = "icons/internal"


class SavedSettings:
    """File/folder names for saved settings."""

    SAVED_SETTINGS_FOLDER = "saved_settings"
    OVEN_PORT = os.path.join(SAVED_SETTINGS_FOLDER, "oven_port.csv")
    SEQUENCE = os.path.join(SAVED_SETTINGS_FOLDER, "sequence_autosave.json")
    SEQUENCE_DIRECTORY = os.path.join(SAVED_SETTINGS_FOLDER, "sequence_directory.csv")


class Oven:
    """File/folder names and dictionary keys for the oven."""

    SETTINGS_FILE = "./oven_settings.json"

    TEMPERATURE_REGISTER = "temperature-register"
    SETPOINT_REGISTER = "setpoint_register"
    MAX_TEMPERATURE = "max-temperature"
    MIN_TEMPERATURE = "min-temperature"
    NUM_DECIMALS = "number-of-decimals"
    STABILITY_TOLERANCE = "stability-tolerance"
    MINIMUM_STABILITY_MEASUREMENTS = "minimum-measurements-for-stability"
    MEASUREMENT_INTERVAL = "measurement-interval"
    STABILITY_MEASUREMENT_INTERVAL = "stability-measurement-interval"


# TODO: murder this
class Sequence:
    """File/folder names for the sequence."""

    # saved settings
    SAVED_SETTINGS = os.path.join(SAVED_SETTINGS_FOLDER, "sequence_settings.csv")
    # folder where data files are stored
    DATA_FOLDER = "Data Files"
    # data files
    PRE_STABLE = "Pre-Stabilization Temperature Data.csv"
    BUFFER = "Buffer Temperature Data.csv"
    STABLE = "Post-Stabilization Temperature Data.csv"
    CYCLE_TIMES = "Cycle Times.csv"
    STABILIZATON_TIMES = "Stabilization Times.csv"
    GRAPH = "Sequence Graph.png"

    # yes this should be nested
    class Headers:
        """Headers for sequence files."""

        DATE_FORMAT = "Day Month Year Hours:Minutes:Seconds AM/PM"
        TIME = "Time (seconds)"
        TEMPERATURE = "Oven Temperature (degrees C)"

    DATETIME_FORMAT_SPECIFIER = (
        Headers.DATE_FORMAT.replace("Day", "%d")
        .replace("Month", "%B")
        .replace("Year", "%Y")
        .replace("Hours", "%I")
        .replace("Minutes", "%M")
        .replace("Seconds", "%S")
        .replace("AM/PM", "%p")
    )  # keep the DATE_FORMAT and its specifier for the `time` module in sync


# TODO: murder this
class InstrumentConnection:
    """File/folder names for instrument connection."""

    PORTS = os.path.join(SAVED_SETTINGS_FOLDER, "ports.csv")


class TreeItem:
    """Dictionary keys for TreeItems."""

    TYPE = "type"
    WIDGET_DATA = "linked-widget-data"
    CHILDREN = "children"


class SequenceBuilder:
    """File/folder names and dictionary keys for the sequence builder."""

    # file/folder names
    OPTIONS_INITIALIZER = "initialization"
    DEFAULT_DATA_FOLDER = "./Data Files"

    DIRECTORY_KEY = "data-directory"

    class Descriptions:
        """File/folder names and dictionary keys for descriptions."""

        FOLDER = "item_descriptions"
        TEMPLATE_FILENAME = "template.md"
        DEFAULT_FOLDER = "default"

        class Overview:
            """Overview section."""

            FILENAME = "overview.md"
            KEY = "OVERVIEW_TEXT"

        class Parameters:
            """Parameters section."""

            FILENAME = "parameters.md"
            KEY = "PARAMETERS_TEXT"

        class Visuals:
            """Visuals section."""

            FILENAME = "visuals.md"
            KEY = "VISUALS_TEXT"

        class DataRecording:
            """Data recording section."""

            FILENAME = "data_recording.md"
            KEY = "DATA_RECORDING_TEXT"


class Datetime:
    HEADER = "Day Month Year Hours:Minutes:Seconds AM/PM"
    FORMAT_SPECIFIER = "%d %B %Y %I:%M:%S %p"


class Process:
    """File/folder names and header text for processes in the sequence builder."""

    class Headers:
        class Time:
            TIME = "Time (seconds)"
            TIME_DATETIME = f"Time ({Datetime.HEADER})"

        class Metadata:
            START_DATETIME = f"Start Time ({Datetime.HEADER})"
            END_DATETIME = f"End Time ({Datetime.HEADER})"
            DURATION = "Duration (seconds)"
            SETPOINT = "Oven Setpoint (degrees C)"

        class Oven:
            TEMPERATURE = "Oven Temperature (degrees C)"

    class Filenames:
        METADATA = "metadata.csv"


FOLDERS_TO_CREATE = [SAVED_SETTINGS_FOLDER, SequenceBuilder.DEFAULT_DATA_FOLDER]
