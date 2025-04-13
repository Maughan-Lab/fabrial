from enum import Enum, Flag, auto, unique, IntEnum


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


class OldSequenceStatus(Flag):
    """States representing the status of a sequence."""

    INACTIVE = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    CANCELED = auto()
    PAUSED = auto()
    ERROR = auto()

    def status_text(self) -> str:
        """Get the status text."""
        if self.name is None:
            return ""
        return self.name.title()

    def color(self) -> str:
        """Get the color (i.e. "green")."""
        match self:
            case OldSequenceStatus.ACTIVE:
                return "green"
            case OldSequenceStatus.PAUSED:
                return "cyan"
            case OldSequenceStatus.ERROR:
                return "red"
            case _:
                return "gray"


@unique
class SequenceStatus(IntEnum):
    """States representing the status of a sequence."""

    INACTIVE = auto()
    ACTIVE = auto()
    COMPLETED = auto()
    CANCELED = auto()
    PAUSED = auto()
    ERROR = auto()
    ERROR_PAUSED = auto()  # there was and error and we paused

    def status_text(self) -> str:
        """Get the status text."""
        match self:
            case SequenceStatus.ERROR_PAUSED:  # ERROR and ERROR_PAUSED use the same text
                return SequenceStatus.ERROR.status_text()
        return self.name.title()

    def is_pause(self) -> bool:
        """Whether this status represents a paused sequence."""
        match self:
            case SequenceStatus.PAUSED | SequenceStatus.ERROR_PAUSED:
                return True
        return False

    def is_error(self) -> bool:
        """Whether this status represents an error state."""
        match self:
            case SequenceStatus.ERROR | SequenceStatus.ERROR_PAUSED:
                return True
        return False

    def is_running(self) -> bool:
        """Whether this status represents a running sequence."""
        match self:
            case SequenceStatus.INACTIVE | SequenceStatus.COMPLETED | SequenceStatus.CANCELED:
                return False
        return True

    def color(self) -> str:
        """Get the color (i.e. "green")."""
        match self:
            case SequenceStatus.ACTIVE:
                return "green"
            case SequenceStatus.PAUSED:
                return "cyan"
            case SequenceStatus.ERROR | SequenceStatus.ERROR_PAUSED:
                return "red"
            case _:
                return "gray"
