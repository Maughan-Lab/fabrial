from PyQt6.QtWidgets import QDoubleSpinBox, QAbstractSpinBox, QSpinBox, QPushButton
from ..instruments import INSTRUMENTS


class DoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox class without up/down buttons."""

    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

    def connect_to_button(self, button: QPushButton):
        """
        Emit the **button**'s **pressed** signal when Enter is pressed and the button is enabled.
        """
        line_edit = self.lineEdit()
        if line_edit is not None:
            line_edit.returnPressed.connect(
                lambda: button.pressed.emit() if button.isEnabled() else None
            )


class TemperatureSpinBox(DoubleSpinBox):
    """DoubleSpinBox for temperatures."""

    def __init__(self):
        """:param oven: The oven to use for setting the maximum/minimum temperatures."""
        super().__init__()
        # temperatures must be between MIN and MAX degrees C
        oven = INSTRUMENTS.oven
        self.setMinimum(oven.minimum_temperature())
        self.setMaximum(oven.maximum_temperature())
        self.setSingleStep(10)  # using the up/down arrow keys will change the temperature by 10
        self.setDecimals(1)


class SpinBox(QSpinBox):
    """QSpinBox class without up/down buttons."""

    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
