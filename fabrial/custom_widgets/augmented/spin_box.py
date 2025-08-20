import sys

from PyQt6.QtWidgets import QAbstractSpinBox, QDoubleSpinBox, QPushButton, QSpinBox


class DoubleSpinBox(QDoubleSpinBox):
    """
    `QDoubleSpinBox` without up/down buttons.

    Parameters
    ----------
    number_of_decimals
        The number of decimals to display.
    minimum
        The minimum allowed value (default 0).
    maximum
        The maximum allowed value (default largest possible float).
    initial_value
        The initial value of the spinbox (default higher of 0 and **minimum**).
    """

    LARGEST_FLOAT = sys.float_info.max

    def __init__(
        self,
        number_of_decimals: int = 1,
        minimum: float = 0,
        maximum: float = LARGEST_FLOAT,
        initial_value: float = 0,
    ):
        QDoubleSpinBox.__init__(self)
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setDecimals(number_of_decimals)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(initial_value)

    def connect_to_button(self, button: QPushButton):
        """
        Emit the **button**'s `pressed` signal when Enter is pressed and the button is enabled.
        """
        line_edit = self.lineEdit()
        if line_edit is not None:
            line_edit.returnPressed.connect(
                lambda: button.pressed.emit() if button.isEnabled() else None
            )


class SpinBox(QSpinBox):
    """
    `QSpinBox` class without up/down buttons.

    Parameters
    ----------
    minimum
        The minimum allowed value (default 0).
    maximum
        The maximum allowed value (default largest possible integer).
    initial_value
        The initial value of the spinbox (default higher of 0 and **minimum**).
    """

    LARGEST_INTEGER = 2147483647

    def __init__(self, minimum: int = 0, maximum: int = LARGEST_INTEGER, initial_value: int = 0):
        QSpinBox.__init__(self)
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setValue(initial_value)
