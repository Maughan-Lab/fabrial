from dataclasses import dataclass
from PyQt6.QtCore import pyqtSignal, QObject
import minimalmodbus as modbus


class Instrument(QObject):
    """Abstract class to represent instruments."""

    # signals
    connectionChanged = pyqtSignal(bool)  # True if connected False if disconnected
    lockChanged = pyqtSignal(bool)  # True if unlocked False if locked

    def __init__(self):
        super().__init__()
        self.connected = False
        # you should only ever read this value, never set it manually
        self.unlocked = True

    def release(self):
        """Make the instrument mutable for other process."""
        self.unlocked = True
        self.lockChanged.emit(self.is_unlocked())

    def acquire(self):
        """Make the instrument mutable for only one process."""
        self.unlocked = False
        self.lockChanged.emit(self.is_unlocked())

    def is_connected(self) -> bool:
        """Get the connection status of this instrument as a bool."""
        return self.connected

    def is_unlocked(self) -> bool:
        """Get the lock status of this instrument as a bool."""
        return self.unlocked


class Oven(Instrument):
    """Class to represent the physical oven Quincy controls."""

    # TODO: remove these when you use pyserial
    SETPOINT_REGISTER = 0
    TEMPERATURE_REGISTER = 1
    NUMBER_OF_DECIMALS = 1

    MINIMUM_TEMPERATURE = 0.0
    MAXIMUM_TEMPERATURE = 232.0

    def __init__(self, oven_port: str):
        super().__init__()
        self.port = oven_port
        self.connect()

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if the oven is connected, None otherwise."""
        try:
            temperature = self.device.read_register(
                self.TEMPERATURE_REGISTER, self.NUMBER_OF_DECIMALS
            )
            return temperature
        except Exception:
            self.update_connection_status(False)
            return None

    def change_setpoint(self, setpoint: float):
        """Sets the oven's temperature to **setpoint**."""
        try:
            self.device.write_register(self.SETPOINT_REGISTER, setpoint, self.NUMBER_OF_DECIMALS)
        except Exception:
            self.update_connection_status(False)

    def get_setpoint(self) -> float | None:
        """Returns the oven's setpoint if the oven is connected, None otherwise."""
        try:
            setpoint = self.device.read_register(self.SETPOINT_REGISTER, self.NUMBER_OF_DECIMALS)
            return setpoint
        except Exception:
            self.update_connection_status(False)
            return None

    def connect(self):
        """Attempts to connect to the oven."""
        try:
            self.device = modbus.Instrument(self.port, 1)
            connected = True
        except Exception:
            connected = False
        self.update_connection_status(connected)

    def update_connection_status(self, connected: bool):
        self.connected = connected
        self.connectionChanged.emit(self.is_connected())

    def update_port(self, port: str):
        """Updates the oven's connection port."""
        self.port = port
        self.connect()


@dataclass
class InstrumentSet:
    """Container for instruments (ovens, potentiostats, etc.)"""

    oven: Oven
    potentiostat: None
