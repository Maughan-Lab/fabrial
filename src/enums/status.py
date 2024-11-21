from enum import Enum


class StabilityStatus(Enum):
    """States representing oven stability."""

    STABLE = 0
    BUFFERING = 1
    UNSTABLE = 2
    CHECKING = 3
    ERROR = 4
    NULL = 5


# dictionaries to translate a StabilityStatus
STABILITY_COLOR_KEY = {
    StabilityStatus.STABLE: "green",
    StabilityStatus.BUFFERING: "cyan",
    StabilityStatus.UNSTABLE: "red",
    StabilityStatus.CHECKING: "orange",
    StabilityStatus.ERROR: "red",
    StabilityStatus.NULL: "",
}

STABILITY_TEXT_KEY = {
    StabilityStatus.STABLE: "Stable",
    StabilityStatus.BUFFERING: "Buffering",
    StabilityStatus.UNSTABLE: "Unstable",
    StabilityStatus.CHECKING: "Checking...",
    StabilityStatus.ERROR: "Error",
    StabilityStatus.NULL: "-----------",
}


class SequenceStatus(Enum):
    """States representing the status of a sequence."""

    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    CANCELED = 3
    PAUSED = 4


# dictionaries to translate a SequenceStatus
SEQUENCE_COLOR_KEY = {
    SequenceStatus.INACTIVE: "gray",
    SequenceStatus.ACTIVE: "green",
    SequenceStatus.COMPLETED: "gray",
    SequenceStatus.CANCELED: "gray",
    SequenceStatus.PAUSED: "cyan",
}

SEQUENCE_TEXT_KEY = {
    SequenceStatus.INACTIVE: "Inactive",
    SequenceStatus.ACTIVE: "Active",
    SequenceStatus.COMPLETED: "Completed",
    SequenceStatus.CANCELED: "Canceled",
    SequenceStatus.PAUSED: "Paused",
}
