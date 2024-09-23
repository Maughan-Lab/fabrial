from PyQt6.QtWidgets import QDoubleSpinBox, QAbstractSpinBox, QSpinBox, QWidget

# constants
MINIMUM_TEMPERATURE = 0
MAXIMUM_TEMPERATURE = 232


# QDoubleSpinBox class without up/down buttons.
class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)


# DoubleSpinBox for temperatures.
class TemperatureSpinBox(DoubleSpinBox):
    def __init__(self):
        super().__init__()
        # temperatures must be between 0 and 232 degrees C
        self.setMinimum(MINIMUM_TEMPERATURE)
        self.setMaximum(MAXIMUM_TEMPERATURE)
        self.setSingleStep(10)  # using the up/down arrow keys will change the temperature by 10


# QSpinBox class without up/down buttons.
class SpinBox(QSpinBox):
    def __init__(self):
        super().__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)


# SpinBox for hours.
class HoursSpinBox(SpinBox):
    def __init__(self):
        super().__init__()
        self.setMinimum(0)


# SpinBox for minutes.
class MinutesSpinBox(SpinBox):
    def __init__(self):
        super().__init__()
        self.setSingleStep(5)  # using the up/down arrow keys will change the minutes by 5
        self.setMinimum(0)
        self.setMaximum(59)
