from PyQt6.QtWidgets import QProgressBar


class ProgressBar(QProgressBar):
    """QProgressBar with easier methods."""

    def __init__(self, minimum: int, maximum: int, increment_value: int = 1):
        """
        :param minimum: The minimum value of the progressbar.
        :param maximum: The maximum value of the progressbar.
        :param increment_value: How much increment() increments the value by. Defaults to 1.
        """
        super().__init__()
        self.increment_value = increment_value
        self.setMinimum(minimum)
        self.setMaximum(maximum)

    def increment(self):
        """Increment the progressbar."""
        self.setValue(self.value() + self.increment_value)
