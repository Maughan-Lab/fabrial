from fabrial import PluginCategory, PluginSettingsWidget

# notice we import our item
from .random_item import RandomDataItem
from .settings import RandomDataSettingsWidget, load_settings


def categories() -> list[PluginCategory]:
    # we use "Random" as the name of the category
    # when creating the `RandomDataItem`, we use 5 as the default value
    return [PluginCategory("Random", [RandomDataItem(5)])]


# this is the entry point for settings widgets
def settings_widget() -> PluginSettingsWidget:
    load_settings()  # load the settings when the widget is being initialized
    return RandomDataSettingsWidget()
