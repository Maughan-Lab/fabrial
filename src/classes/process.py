from dataclasses import dataclass
from ..instruments import InstrumentSet
from PyQt6.QtCore import QThreadPool


@dataclass
class ProcessInputs:
    """Contains items for the `run()` method of item Processes."""

    instrument_set: InstrumentSet
    threadpool: QThreadPool
