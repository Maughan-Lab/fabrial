from .saved_data import CORE_SETTINGS_FOLDER

PLUGIN_SETTINGS_FOLDER = CORE_SETTINGS_FOLDER.joinpath("plugins")
LOCAL_PLUGINS_FILE = PLUGIN_SETTINGS_FOLDER.joinpath("local_plugins.json")
GLOBAL_PLUGINS_FILE = PLUGIN_SETTINGS_FOLDER.joinpath("global_plugins.json")
