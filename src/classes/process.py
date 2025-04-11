from ..instruments import InstrumentSet
from PyQt6.QtCore import QThreadPool
from ..sequence_builder.tree_item import TreeItem


class ProcessInputs:
    """Contains items for the `run()` method of item Processes."""

    def __init__(self, instruments: InstrumentSet, data_directory: str):
        """
        :param instruments: The application's instruments.
        :param data_directory: The folder where all sequence data will be stored.
        """
        self.instruments = instruments
        self.data_directory = data_directory
        self.threadpool = QThreadPool()
        self.current_item: TreeItem | None = None

    def set_current_item(self, item: TreeItem):
        """Set the current item. This updates the item's `running` parameter."""
        if self.current_item is not None:
            self.current_item.set_running(False)
        self.current_item = item
        self.current_item.set_running(True)

    def __del__(self):
        """The sequence has ended, so tell the current item it is no longer running."""
        if self.current_item is not None:
            self.current_item.set_running(False)
