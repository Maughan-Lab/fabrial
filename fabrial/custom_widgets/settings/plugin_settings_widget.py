from PyQt6.QtWidgets import QWidget


class PluginSettingsWidget(QWidget):
    """
    A widget base class that plugins can use for settings.

    Has the `window_open_event()` and `window_close_event()` methods that get called whenever the
    settings menu window is opened and closed, respectively. You can override these to load and save
    settings, for example.
    """

    def window_open_event(self):
        """Called when the settings window is opened. Does nothing by default."""
        return

    def window_close_event(self):
        """Called when the settings window is closed. Does nothing by default."""
        return
