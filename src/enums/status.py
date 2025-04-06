from enum import Enum, unique, auto


class StabilityStatus(Enum):
    """States representing stability."""

    # non-specified values will be filled in by the constructor

    # NAME = color, status text, legend text (optional), truth value (optional)
    STABLE = "green", "Stable", "Stable", True
    BUFFERING = "cyan", "Buffering", "Buffer"
    UNSTABLE = "red", "Unstable"
    CHECKING = "orange", "Checking...", "Pre-Stable"
    ERROR = "red", "Error"
    NULL = "", "-----------"

    def __init__(
        self, color: str, status_text: str, legend_text: str = "", truth_value: bool = False
    ):
        self.color = color
        self.status_text = status_text
        self.legend_text = legend_text
        self.truth_value = truth_value

    def __bool__(self):
        """Return a boolean representation of stability."""
        return self.truth_value


class SequenceStatus(Enum):
    """States representing the status of a sequence."""

    INACTIVE = "gray", "Inactive"
    ACTIVE = "green", "Active", True
    COMPLETED = "gray", "Completed"
    CANCELED = "gray", "Cancelled"
    PAUSED = "cyan", "Paused", True
    ERROR = "red", "Error"

    def __init__(self, color: str, status_text: str, truth_value: bool = False):
        self.color = color
        self.status_text = status_text
        self.truth_value = truth_value

    def __bool__(self):
        """Return a boolean representing the running state."""
        return self.truth_value
