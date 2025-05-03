"""File and folder locations for the whole application."""

import os

APPLICATION_NAME = "Quincy"
SAVED_SETTINGS_FOLDER = "saved_settings"
APPLICATION_SETTINGS_FOLDER = "application_settings"
DEFAULT_GAMRY_LOCATION = "C:/Program Files (x86)/Gamry Instruments/Framework/GamryCom.exe"


class Icons:
    """Icon file/folder names."""

    MAIN_ICON = "icons/oven_icon.png"
    INTERNAL_ICONS = "icons/internal"


class SavedSettings:
    """File/folder names for saved settings."""

    OVEN_PORT = os.path.join(SAVED_SETTINGS_FOLDER, "oven_port.csv")

    class Sequence:
        """Saved settings for the sequence."""

        FOLDER = os.path.join(SAVED_SETTINGS_FOLDER, "sequence")

        SEQUENCE_AUTOSAVE = os.path.join(FOLDER, "sequence_autosave.json")
        OPTIONS_STATE_AUTOSAVE = os.path.join(FOLDER, "options_state_autosave.json")
        SEQUENCE_DIRECTORY = os.path.join(FOLDER, "sequence_directory.csv")
        NON_EMPTY_DIRECTORY_WARNING = os.path.join(FOLDER, "non_empty_directory_warning.csv")


class ApplicationSettings:
    """File/folder names for application-level settings."""

    class Oven:
        """File names and dictionary keys for oven settings."""

        FOLDER = os.path.join(APPLICATION_SETTINGS_FOLDER, "oven")
        SETTINGS_FILE = os.path.join(FOLDER, "oven_settings.json")
        DESCRIPTION_FILENAME = "description.md"

        TEMPERATURE_REGISTER = "Temperature Register"
        SETPOINT_REGISTER = "Setpoint Register"
        MAX_TEMPERATURE = "Maximum Temperature"
        MIN_TEMPERATURE = "Minimum Temperature"
        NUM_DECIMALS = "Number of Decimals"
        STABILITY_TOLERANCE = "Stability Tolerance"
        MEASUREMENT_INTERVAL = "Measurement Interval (ms)"
        MINIMUM_STABILITY_MEASUREMENTS = "Minimum Measurements for Stability"
        STABILITY_MEASUREMENT_INTERVAL = "Stability Check Interval (ms)"

    class Gamry:
        """File names and dictionary keys for Gamry settings."""

        FOLDER = os.path.join(APPLICATION_SETTINGS_FOLDER, "gamry")
        SETTINGS_FILE = os.path.join(FOLDER, "gamry_settings.json")
        DESCRIPTION_FILENAME = "description.md"

        ENABLED = "Enabled"
        LOCATION = "GamryCOM Location"


class TreeItem:
    """Dictionary keys for **TreeItem**s."""

    TYPE = "type"
    WIDGET_DATA = "linked-widget-data"
    CHILDREN = "children"

    DEFAULT_ICON_FILENAME = "script.png"


class TreeView:
    """Dictionary keys for **TreeView**s."""

    ITEM_DATA = "item-data"
    VIEW_DATA = "view-data"
    EXPANDED = "expanded"


class SequenceBuilder:
    """File/folder names and dictionary keys for the sequence builder."""

    # file/folder names
    OPTIONS_INITIALIZER = "item_initialization"
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

            DIRECTORY_KEY = "DIRECTORY_NAME"
            METADATA_KEY = "METADATA_FILE"


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
        TEMPERATURES = "temperature.csv"


FOLDERS_TO_CREATE = [
    SAVED_SETTINGS_FOLDER,
    SavedSettings.Sequence.FOLDER,
    SequenceBuilder.DEFAULT_DATA_FOLDER,
]
