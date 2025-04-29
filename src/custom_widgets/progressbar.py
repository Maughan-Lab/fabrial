from PyQt6.QtWidgets import QProgressBar, QWidget
from ..instruments import Oven


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


class StabilityProgressBar(QProgressBar):
    """QProgressBar for oven stability."""

    def __init__(self, oven: Oven, parent: QWidget | None = None):
        """
        Automatically sets the minimum and maximum based on the oven.

        :param oven: The oven to base the maximum on.
        :param parent: The widget's parent.
        """
        super().__init__(parent)
        self.setMinimum(0)
        self.setMaximum(oven.minimum_measurements())

    def sizeHint(self):
        size = super().sizeHint()
        size.setWidth(size.width() * 2)  # arbitrary, this just looks better
        return size
