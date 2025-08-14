from enum import Enum, IntEnum, auto, unique


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

    @staticmethod
    def bool_to_str(stable: bool):
        """Convert a bool representing stability to text."""
        if stable:
            return "Stable"
        return "Not Stable"

    @staticmethod
    def bool_to_color(stable: bool):
        """Convert a bool representing stability to a color string."""
        if stable:
            return "green"
        return "red"


class ConnectionStatus(Enum):
    """Enum to represent connection states."""

    CONNECTED = 0
    DISCONNECTED = 1
    NULL = 2

    def __bool__(self):
        return self == ConnectionStatus.CONNECTED

    @staticmethod
    def bool_to_str(connected: bool) -> str:
        """Convert a bool representing the connection status to text."""
        if connected:
            return "Connected"
        return "Disconnected"

    @staticmethod
    def bool_to_color(connected: bool) -> str:
        """Convert a bool representing the connection status to a color string."""
        if connected:
            return "green"
        return "red"


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


class StatusStateMachine:
    """
    Container for a SequenceStatus. This defines valid state transitions. If you try to set the
    state to an invalid state, it will be ignored.

    Parameters
    ----------
    initial_status
        The initial status.
    """

    def __init__(self, initial_status: SequenceStatus):
        self.status = initial_status

    def set(self, status: SequenceStatus) -> bool:
        """
        Set the internal status without emitting signals.

        Returns
        -------
        `True` if the status changed (a valid state transition occurred), `False` otherwise.
        """
        match self.status:
            case SequenceStatus.INACTIVE | SequenceStatus.COMPLETED | SequenceStatus.CANCELED:
                # these can only go to ACTIVE
                match status:
                    case SequenceStatus.ACTIVE:
                        pass
                    case _:
                        return False
            case SequenceStatus.ACTIVE | SequenceStatus.PAUSED:
                # ACTIVE and PAUSED can go to any state
                pass
            case SequenceStatus.ERROR_PAUSED:
                # ERROR_PAUSED cannot go to PAUSED or ERROR
                match status:
                    case SequenceStatus.PAUSED | SequenceStatus.ERROR:
                        return False
            case SequenceStatus.ERROR:
                # ERROR cannot go to PAUSED
                match status:
                    case SequenceStatus.PAUSED:
                        return False
                    case _:
                        pass
        # if we made it here we are performing a valid state transition
        self.status = status
        return True

    def get(self) -> SequenceStatus:
        """Get the status."""
        return self.status
