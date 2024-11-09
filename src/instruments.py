from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import pyqtSignal, QObject


class ConnectionStatus(Enum):
    DISCONNECTED = 0
    CONNECTED = 1
    NULL = 2


CONNECTION_COLOR_KEY = {
    ConnectionStatus.DISCONNECTED: "red",
    ConnectionStatus.CONNECTED: "green",
    ConnectionStatus.NULL: "gray",
}


class Instrument(QObject):
    """Abstract class to represent instruments."""

    # signals
    connectionChanged = pyqtSignal(bool)  # True if connected False if disconnected
    lockChanged = pyqtSignal(bool)  # True if unlocked False if locked

    def __init__(self):
        super().__init__()
        self.connection_status = ConnectionStatus.NULL
        # you should only ever read this value, never set it manually
        self.unlocked = True

    def release(self):
        """Make the instrument mutable for other process."""
        self.unlocked = True

    def aquire(self):
        """Make the instrument mutable for only one process."""
        self.unlocked = False


# TODO: implement temperature sensor reading with PySerial
# import serial
class Oven(Instrument):
    """Class to represent the physical oven Quincy controls."""

    MINIMUM_TEMPERATURE = 0.0
    MAXIMUM_TEMPERATURE = 232.0

    def __init__(self, oven_port: str):
        super().__init__()
        self.port = oven_port

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if the oven is connected, None otherwise."""
        if self.connection_status == ConnectionStatus.CONNECTED:
            return 1  # TODO: implement actually reading the temperature
        else:
            return None

    def change_setpoint(self, setpoint: float):
        """Sets the oven's temperature to `setpoint`."""
        pass

    def get_setpoint(self) -> float | None:
        """Returns the oven's setpoint if the oven is connected, None otherwise."""
        if self.connection_status == ConnectionStatus.CONNECTED:
            return 1  # TODO: implement actually reading the setpoint
        else:
            return None

    def connect(self):
        """Attempts to connect to the oven. A failed attempt will set `connected` to False."""
        # TODO: implement the connection
        new_connection_status = ConnectionStatus.DISCONNECTED

        if self.connection_status != new_connection_status:
            self.connection_status = new_connection_status
            self.connectionChanged.emit(self.connection_status == ConnectionStatus.CONNECTED)

    def update_port(self, port: str):
        """Updates the oven's connection port."""
        self.port = port
        self.connect()


@dataclass
class InstrumentSet:
    """Container for instruments (the oven, potentiostats, etc.)"""

    oven: Oven
    potentiostat: None
