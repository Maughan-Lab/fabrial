from PyQt6.QtWidgets import QDoubleSpinBox, QAbstractSpinBox, QSpinBox, QPushButton
from ..instruments import Oven


class DoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox class without up/down buttons."""

    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

    def connect_to_button(self, button: QPushButton):
        """
        Emit the **button**'s **pressed** signal when Enter is pressed and the button is enabled.
        """
        lineedit = self.lineEdit()
        if lineedit is not None:
            lineedit.returnPressed.connect(
                lambda: button.pressed.emit() if button.isEnabled() else None
            )


class TemperatureSpinBox(DoubleSpinBox):
    """DoubleSpinBox for temperatures."""

    def __init__(self):
        super().__init__()
        # temperatures must be between 0 and 232 degrees C
        self.setMinimum(Oven.MINIMUM_TEMPERATURE)
        self.setMaximum(Oven.MAXIMUM_TEMPERATURE)
        self.setSingleStep(10)  # using the up/down arrow keys will change the temperature by 10
        self.setDecimals(1)


class SpinBox(QSpinBox):
    """QSpinBox class without up/down buttons."""

    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
