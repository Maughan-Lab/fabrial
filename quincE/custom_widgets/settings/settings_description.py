from PyQt6.QtWidgets import QLayout

from ..parameter_description import ParameterDescriptionWidget


class SettingsDescriptionWidget(ParameterDescriptionWidget):
    """Widget with two tabs: one for settings and one for description text."""

    def __init__(self, parameter_layout: QLayout | None = None):
        ParameterDescriptionWidget.__init__(self, parameter_layout, "Settings")
