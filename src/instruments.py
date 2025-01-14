from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import pyqtSignal, QObject
import minimalmodbus as modbus
from mutex import SignalMutex
from typing import Union, TYPE_CHECKING
from utility.timers import Timer

if TYPE_CHECKING:
    from developer import DeveloperOven


def to_str(connected: bool) -> str:
    """Convert a bool representing the connection status to text."""
    if connected:
        return "CONNECTED"
    else:
        return "DISCONNECTED"


def to_color(connected: bool) -> str:
    """Convert a bool representing the connection status to a color string."""
    if connected:
        return "green"
    else:
        return "red"


class ConnectionStatus(Enum):
    """Enum to represent connection states."""

    CONNECTED = 0
    DISCONNECTED = 1
    NULL = 2

    def __bool__(self):
        return self == ConnectionStatus.CONNECTED


class Instrument(QObject):
    """
    Abstract class to represent instruments. When using methods that change the physical oven,
    call acquire() followed at some point by release().
    """

    # signals
    connectionChanged = pyqtSignal(bool)  # True if connected False if disconnected

    def __init__(self):
        super().__init__()
        self.__connection_status = ConnectionStatus.NULL

        # lock system
        self.lock = SignalMutex()  # do not manually access the lock ever
        self.lockChanged = self.lock.lockChanged  # shortcut to signal inside self.lock

    def acquire(self):
        """
        Make the instrument mutable for only one process. This should be followed by a call to
        **release()**.
        """
        self.lock.lock()

    def release(self):
        """Make the instrument mutable for other processes."""
        self.lock.unlock()

    def update_connection_status(self, connection_status: ConnectionStatus):
        """
        Helper function to update the connection status and emit a signal. This should not be
        called outside of the oven.
        """
        if self.__connection_status != connection_status:
            self.__connection_status = connection_status
            self.connectionChanged.emit(self.is_connected())

    def is_connected(self) -> bool:
        """Get the connection status of this instrument as a bool."""
        return bool(self.__connection_status)

    def is_unlocked(self) -> bool:
        """Get the lock status of this instrument as a bool."""
        acquired = self.lock.tryLock()
        if acquired:
            self.lock.unlock()
        return acquired


class Oven(Instrument):
    """Class to represent the physical oven Quincy controls."""

    # signals
    temperatureChanged = pyqtSignal(float)
    setpointChanged = pyqtSignal(float)

    SETPOINT_REGISTER = 0
    TEMPERATURE_REGISTER = 1
    NUMBER_OF_DECIMALS = 1

    MINIMUM_TEMPERATURE = 0.0
    MAXIMUM_TEMPERATURE = 232.0

    def __init__(self, oven_port: str = ""):
        super().__init__()
        # the __ before variables just means they should not be read directly (private)
        self.__device: modbus.Instrument | None = None
        self.__port = oven_port
        self.__temperature: float = -1
        self.__setpoint: float = -1

        self.temperature_timer = Timer(self, 1000, self.read_temp)
        self.setpoint_timer = Timer(self, 1000, self.get_setpoint)

        self.connection_timer = Timer(self, 1000, self.connect)
        self.connectionChanged.connect(self.handle_connection_change)
        self.connection_timer.start()

    def handle_connection_change(self, connected: bool):
        if connected:
            self.connection_timer.stop()
            self.temperature_timer.start()
            self.setpoint_timer.start()
        else:
            self.temperature_timer.stop()
            self.setpoint_timer.stop()
            self.__temperature = -1
            self.__setpoint = -1
            self.connection_timer.start()

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if the oven is connected, None otherwise."""
        print("READING TEMPERATURE")
        try:
            temperature = self.__device.read_register(
                self.TEMPERATURE_REGISTER, self.NUMBER_OF_DECIMALS
            )
            if temperature != self.__temperature:
                self.__temperature = temperature
                self.temperatureChanged.emit(temperature)
            return temperature
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
            return None

    def change_setpoint(self, setpoint: float) -> bool:
        """
        Sets the oven's temperature to **setpoint**. Returns a bool indicating whether the operation
        was successful.
        """
        try:
            self.__device.write_register(self.SETPOINT_REGISTER, setpoint, self.NUMBER_OF_DECIMALS)
            self.__setpoint = setpoint
            self.setpointChanged.emit(setpoint)
            return True
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        return False

    def get_setpoint(self) -> float | None:
        """Returns the oven's setpoint if the oven is connected, None otherwise."""
        print("READING SETPOINT")
        try:
            setpoint = self.__device.read_register(self.SETPOINT_REGISTER, self.NUMBER_OF_DECIMALS)
            if setpoint != self.__setpoint:
                self.__setpoint = setpoint
                self.setpointChanged.emit(setpoint)
            return setpoint
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
            return None

    def connect(self):
        """Attempts to connect to the oven."""
        try:
            del self.__device
            self.__device = modbus.Instrument(self.__port, 1, close_port_after_each_call=True)
            connection_status = ConnectionStatus.CONNECTED
            print("CONNECTED")
        except Exception:
            connection_status = ConnectionStatus.DISCONNECTED
            print("NOT CONNECTED")
        self.update_connection_status(connection_status)

    def update_port(self, port: str):
        """Updates the oven's connection port."""
        self.__port = port
        self.connect()


@dataclass
class InstrumentSet:
    """Container for instruments (ovens, potentiostats, etc.)"""

    oven: Union[Oven, "DeveloperOven"]
    potentiostat: None
