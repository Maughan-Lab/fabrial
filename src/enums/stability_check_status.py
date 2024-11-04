from enum import Enum


class StabilityCheckStatus(Enum):
    """
    Enum to represent the different instrument stability states.
    """

    STABLE = 0
    UNSTABLE = 1
    ERROR = 2
    PAUSED = 3
    CANCELED = 4
    CHECKING = 5
    BUFFERING = 6
    NULL = 7
