"""File and folder locations for the whole application."""

from dataclasses import dataclass
from os import path


SAVED_SETTINGS_FOLDER = "saved_settings"
ICON = "icons/oven_icon.png"


@dataclass
class Sequence:
    """File/folder names for the sequence."""

    # saved settings
    SAVED_SETTINGS = path.join(SAVED_SETTINGS_FOLDER, "sequence_settings.csv")
    # folder where data files are stored
    DATA_FOLDER = "Data Files"
    # data files
    PRE_STABLE = "Pre-Stabilization Temperature Data.csv"
    BUFFER = "Buffer Temperature Data.csv"
    STABLE = "Post-Stabilization Temperature Data.csv"
    CYCLE_TIMES = "Cycle Times.csv"
    STABILIZATON_TIMES = "Stabilization Times.csv"
    GRAPH = "Sequence Graph.jpeg"

    # yes this should be nested
    @dataclass
    class Headers:
        """Headers for sequence files."""

        DATE_FORMAT = "Day Month Year Hours:Minutes:Seconds AM/PM"
        TIME = "Time (seconds)"
        TEMPERATURE = "Oven Temperature (degrees C)"


@dataclass
class InstrumentConnection:
    """File/folder names for instrument connection."""

    PORTS = path.join(SAVED_SETTINGS_FOLDER, "ports.csv")
