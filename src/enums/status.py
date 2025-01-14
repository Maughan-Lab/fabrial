from enum import Enum


class StabilityStatus(Enum):
    """States representing stability."""

    STABLE = 0
    BUFFERING = 1
    UNSTABLE = 2
    CHECKING = 3
    ERROR = 4
    NULL = 5

    def to_color(self) -> str:
        """Return a color (string) representation."""
        match self:
            case StabilityStatus.STABLE:
                return "green"
            case StabilityStatus.BUFFERING:
                return "cyan"
            case StabilityStatus.UNSTABLE | StabilityStatus.ERROR:
                return "red"
            case StabilityStatus.CHECKING:
                return "orange"
            case StabilityStatus.NULL:
                return ""

    def __str__(self):
        """Return a text representation."""
        match self:
            case StabilityStatus.CHECKING:
                return "Checking..."
            case StabilityStatus.NULL:
                return "-----------"
            case _:
                return self.name.capitalize()

    def __bool__(self):
        """Return a boolean representation of stability."""
        match self:
            case StabilityStatus.STABLE:
                return True
            case _:
                return False


class SequenceStatus(Enum):
    """States representing the status of a sequence."""

    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    CANCELED = 3
    PAUSED = 4

    def to_color(self) -> str:
        """Return a color (string) representation."""
        match self:
            case SequenceStatus.INACTIVE | SequenceStatus.COMPLETED | SequenceStatus.CANCELED:
                return "gray"
            case SequenceStatus.ACTIVE:
                return "green"
            case SequenceStatus.PAUSED:
                return "cyan"

    def __str__(self):
        """Return a text representation."""
        return self.name.capitalize()

    def __bool__(self):
        """Return a boolean representing the running state."""
        match self:
            case SequenceStatus.ACTIVE | SequenceStatus.PAUSED:
                return True
            case _:
                return False
