from PyQt6.QtWidgets import QProgressBar


class ProgressBar(QProgressBar):
    """
    `QProgressBar` with easier methods.

    Parameters
    ----------
    minimum
        The minimum value of the progressbar.
    maximum
        The maximum value of the progressbar.
    increment_value
        How much increment() increments the value by. Defaults to 1.
    """

    def __init__(self, minimum: int, maximum: int, increment_value: int = 1):
        QProgressBar.__init__(self)
        self.increment_value = increment_value
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    def increment(self):
        """Increment the progressbar."""
        self.setValue(self.value() + self.increment_value)
