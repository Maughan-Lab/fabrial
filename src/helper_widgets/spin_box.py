from PyQt6.QtWidgets import QDoubleSpinBox, QAbstractSpinBox, QSpinBox

# constants
MINIMUM_TEMPERATURE = 0
MAXIMUM_TEMPERATURE = 232


class DoubleSpinBox(QDoubleSpinBox):
    """QDoubleSpinBox class without up/down buttons."""

    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)


class TemperatureSpinBox(DoubleSpinBox):
    """DoubleSpinBox for temperatures."""

    def __init__(self):
        super().__init__()
        # temperatures must be between 0 and 232 degrees C
        self.setMinimum(MINIMUM_TEMPERATURE)
        self.setMaximum(MAXIMUM_TEMPERATURE)
        self.setSingleStep(10)  # using the up/down arrow keys will change the temperature by 10
        self.setDecimals(1)


class SpinBox(QSpinBox):
    """QSpinBox class without up/down buttons."""

    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)


class HoursSpinBox(SpinBox):
    """SpinBox for hours."""

    def __init__(self):
        super().__init__()
        self.setMinimum(0)


class MinutesSpinBox(SpinBox):
    """SpinBox for minutes."""

    def __init__(self):
        super().__init__()
        self.setSingleStep(5)  # using the up/down arrow keys will change the minutes by 5
        self.setMinimum(0)
        self.setMaximum(59)
