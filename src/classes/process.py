from dataclasses import dataclass
from ..instruments import InstrumentSet
from PyQt6.QtCore import QThreadPool
from ..sequence_builder.tree_item import TreeItem


@dataclass
class ProcessInputs:
    """Contains items for the `run()` method of item Processes."""

    instruments: InstrumentSet
    threadpool: QThreadPool
    data_directory: str
    current_item: TreeItem
