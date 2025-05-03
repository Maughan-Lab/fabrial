import sys

from PyQt6.QtWidgets import QAbstractSpinBox, QDoubleSpinBox, QPushButton, QSpinBox

from ...instruments import Oven


class DoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox class without up/down buttons."""

    LARGEST_FLOAT = sys.float_info.max

    def __init__(
        self,
        number_of_decimals: int = 1,
        minimum: float = 0,
        maximum: float = LARGEST_FLOAT,
        initial_value: int = 0,
    ):
        """
        :param number_of_decimals: The number of decimals to display.
        :param minimum: The minimum allowed value (default 0).
        :param maximum: The maximum allowed value (default largest possible float).
        :param initial_value: The initial value of the spinbox (default higher of 0 and
        **minimum**).
        """
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setDecimals(number_of_decimals)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(initial_value)

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

    def __init__(self, oven: Oven):
        """:param oven: The oven to use for setting the maximum/minimum temperatures."""
        super().__init__(
            oven.num_decimals(), oven.minimum_temperature(), oven.maximum_temperature()
        )


class SpinBox(QSpinBox):
    """QSpinBox class without up/down buttons."""

    LARGEST_INTEGER = 2147483647

    def __init__(self, minimum: int = 0, maximum: int = LARGEST_INTEGER, initial_value: int = 0):
        """
        :param minimum: The minimum allowed value (default 0).
        :param maximum: The maximum allowed value (default largest possible integer).
        :param initial_value: The initial value of the spinbox (default higher of 0 and
        **minimum**).
        """
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(initial_value)
