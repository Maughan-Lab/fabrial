from dataclasses import dataclass
from enum import Enum


class Instrument:
    """Abstract class to represent instruments."""

    def __init__(self):
        # you should only ever read this value, never set it manually
        self.unlocked = True

    def release(self):
        """Make the instrument available for other functions."""
        self.unlocked = True

    def aquire(self):
        """Make the instrument useable by only one function."""
        self.unlocked = False


class Status(Enum):
    """
    Enum to represent the different instrument stability states.
    """

    STABLE = 0
    UNSTABLE = 1
    ERROR = 2
    CANCELED = 3
    CHECKING = 4
    NULL = 5


# TODO: implement temperature sensor reading with PySerial
# import serial
class Oven(Instrument):
    """Class to represent the physical oven Quincy controls."""

    MINIMUM_TEMPERATURE = 0.0
    MAXIMUM_TEMPERATURE = 232.0

    def __init__(self, oven_port: str):
        super().__init__()
        self.port = oven_port
        self.connected = self.connect()
        self.status = Status.NULL

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if the oven is connected, None otherwise."""
        if self.connected:
            return 1  # TODO: implement actually reading the temperature
        else:
            return None

    def change_setpoint(self, setpoint: float):
        """Sets the oven's temperature to `setpoint`."""
        pass

    def get_setpoint(self) -> float | None:
        """Returns the oven's setpoint if the oven is connected, None otherwise."""
        if self.connected:
            return 1  # TODO: implement actually reading the setpoint
        else:
            return None

    def connect(self):
        """Attempts to connect to the oven. A failed attempt will set `connected` to False."""
        # TODO: implement the connection
        self.connected = False

    def update_port(self, port: str):
        """Updates the oven's connection port."""
        self.port = port
        self.connect()


@dataclass
class InstrumentSet:
    """Container for instruments (the oven, potentiostats, etc.)"""

    oven: Oven
    potentiostat: None
