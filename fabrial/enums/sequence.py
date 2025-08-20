from enum import Enum, auto


class SequenceStatus(Enum):
    """Statuses for the sequence."""

    Active = auto()
    Paused = auto()
    Completed = auto()
    Cancelled = auto()
    FatalError = auto()


class SequenceCommand(Enum):
    """Commands that can be send to the sequence thread."""

    Pause = auto()
    Unpause = auto()
    Cancel = auto()
    RaiseFatal = auto()
