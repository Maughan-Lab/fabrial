"""File and folder locations for the whole application."""

import os

SAVED_SETTINGS_FOLDER = "saved_settings"
ICON = "icons/oven_icon.png"


class Icons:
    """Icon os.paths."""

    INTERNAL_ICONS = "icons/internal"


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


class InstrumentConnection:
    """File/folder names for instrument connection."""

    PORTS = os.path.join(SAVED_SETTINGS_FOLDER, "ports.csv")


class TreeItem:
    """Dictionary keys for TreeItems."""

    TYPE = "type"
    WIDGET_DATA = "linked-widget-data"
    CHILDREN = "children"


class SequenceBuilder:
    """File/folder names for the sequence builder."""

    OPTIONS_INITIALIZER = "initialization"
    DESCRIPTIONS = "item_descriptions"
    DEFAULT_DATA_FOLDER = "./Data Files"


class Datetime:
    HEADER = "Day Month Year Hours:Minutes:Seconds AM/PM"
    FORMAT_SPECIFIER = "%d %B %Y %I:%M:%S %p"


class Process:
    """File/folder names and header text for processes in the sequence builder."""

    class Headers:
        class Time:
            # time
            TIME = "Time (seconds)"
            TIME_DATETIME = f"Time ({Datetime.HEADER})"

        class Metadata:
            START_TIME = "Start Time"
            START_TIME_DATETIME = f"{START_TIME} ({Datetime.HEADER})"
            END_TIME = "End Time"
            END_TIME_DATETIME = f"{END_TIME} ({Datetime.HEADER})"

    class Filenames:
        METADATA = "metadata.csv"


FOLDERS_TO_CREATE = [SAVED_SETTINGS_FOLDER, SequenceBuilder.DEFAULT_DATA_FOLDER]
