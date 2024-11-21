from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot

from .constants import (
    CYCLE_COLUMN,
    TEMPERATURE_COLUMN,
    BUFFER_HOURS_COLUMN,
    BUFFER_MINUTES_COLUMN,
    HOLD_HOURS_COLUMN,
    HOLD_MINUTES_COLUMN,
)
from .table_model import TableModel
from polars import col
from enums.status import StabilityStatus, SequenceStatus


class SequenceThread(QRunnable):
    """
    Thread that inherits from **QRunnable**.

    :param fn: The function callback to run on this worker thread.
    :type fn: function
    :param args: Arguments to pass to **fn**.
    :param kwargs: Keywords to pass to **fn**.
    """

    newDataAquired = pyqtSignal(float, float)
    cycleNumberChanged = pyqtSignal(int)
    stabilityChanged = pyqtSignal(StabilityStatus)
    statusChanged = pyqtSignal(SequenceStatus)
    # emit these signals when a cycle/buffer is skipped
    bufferSkipped = pyqtSignal()
    cycleSkipped = pyqtSignal()

    def __init__(self, model: TableModel, fn, *args, **kwargs):
        # TODO: give this class its own signals
        # TODO: make the class accept its initial arguments for the sequence
        super().__init__()
        self.model = model
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self):
        """
        Initialise **fn** with passed **args** and **kwargs**.
        """
        self.fn(*self.args, **self.kwargs)

        # TODO: remember to lock and unlock the oven
