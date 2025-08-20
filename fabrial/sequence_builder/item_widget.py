from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget

from ..custom_widgets import ParameterDescriptionWidget
from ..utility.descriptions import NO_DESCRIPTION_PROVIDED, DescriptionProvider


class ItemWidget(ParameterDescriptionWidget):
    """
    A widget that holds the data and description for a sequence item.

    Parameters
    ----------
    parameter_widget
        The widget to use for the parameter tab. It can be accessed via `parameter_widget()`.
    title
        The window's initial title. This can be changed via `setWindowTitle()` and accessed via
        `windowTitle()`.
    icon
        The windows initial icon. This can be changed via `setWindowIcon()` and accessed via
        `windowIcon()`.
    description_info
        A `DescriptionInfo` to initialize the description tab with. If this is `None`, the
        description tab will have no description.
    """

    def __init__(
        self,
        parameter_widget: QWidget | None,
        title: str,
        icon: QIcon,
        description_provider: DescriptionProvider | None,
    ):
        ParameterDescriptionWidget.__init__(self, parameter_widget)
        self.setWindowTitle(title)
        self.setWindowIcon(icon)
        description = (
            description_provider.render()
            if description_provider is not None
            else NO_DESCRIPTION_PROVIDED
        )
        self.set_description(description)
        self.windowTitle()
        # make it so you have to close this window to access the application
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

    def show_editable(self, editable: bool):
        """Show the widget. If **editable** is `True`, the parameter tab can be edited."""
        if (widget := self.parameter_widget()) is not None:
            widget.setEnabled(editable)
        self.show()
