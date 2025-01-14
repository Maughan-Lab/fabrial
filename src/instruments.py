from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import pyqtSignal, QObject, QMutex
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

        # this lock indicates to the rest of the application the instrument is not available
        self.__lock = SignalMutex()  # do not manually access the lock ever
        self.lockChanged = self.__lock.lockChanged  # shortcut to signal inside self.lock

        # this lock ensures accessing the physical device is thread safe
        self._device_lock = QMutex()

    def acquire(self):
        """
        Make the instrument mutable for only one process. This should be followed by a call to
        **release()**.
        """
        self.__lock.lock()

    def release(self):
        """Make the instrument mutable for other processes."""
        self.__lock.unlock()

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
        acquired = self.__lock.tryLock()
        if acquired:
            self.__lock.unlock()
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
        self.__port = oven_port
        self.__temperature: float = -1
        self.__setpoint: float = -1

        self.__temperature_timer = Timer(self, 1000, self.read_temp)
        self.__setpoint_timer = Timer(self, 1000, self.get_setpoint)

        self.connection_timer = Timer(self, 1000, self.connect)
        self.connectionChanged.connect(self.handle_connection_change)

    def handle_connection_change(self, connected: bool):
        if connected:
            self.connection_timer.stop()
            self.__temperature_timer.start()
            self.__setpoint_timer.start()
        else:
            self.__temperature_timer.stop()
            self.__setpoint_timer.stop()
            self.__temperature = -1
            self.__setpoint = -1
            self.connection_timer.start()

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if on a successful read, None otherwise."""
        if not self._device_lock.tryLock():
            return None
        temperature: float | None = None

        try:
            temperature = float(
                self.__device.read_register(self.TEMPERATURE_REGISTER, self.NUMBER_OF_DECIMALS)
            )
            if temperature != self.__temperature:
                self.__temperature = temperature
                self.temperatureChanged.emit(temperature)
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
            return None
        finally:
            self._device_lock.unlock()

        return temperature

    def change_setpoint(self, setpoint: float) -> bool:
        """
        Sets the oven's temperature to **setpoint**. Returns True if the operation was successful,
        False otherwise.
        """
        if not self._device_lock.tryLock():
            return False
        success = False

        try:
            self.__device.write_register(self.SETPOINT_REGISTER, setpoint, self.NUMBER_OF_DECIMALS)
            self.__setpoint = setpoint
            self.setpointChanged.emit(setpoint)
            success = True
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        finally:
            self._device_lock.unlock()

        return success

    def get_setpoint(self) -> float | None:
        """Returns the oven's setpoint if on a successful read, None otherwise."""
        if not self._device_lock.tryLock():
            return None
        setpoint: float | None = None

        try:
            setpoint = float(
                self.__device.read_register(self.SETPOINT_REGISTER, self.NUMBER_OF_DECIMALS)
            )
            if setpoint != self.__setpoint:
                self.__setpoint = setpoint
                self.setpointChanged.emit(setpoint)

        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        finally:
            self._device_lock.unlock()

        return setpoint

    def connect(self):
        """Attempts to connect to the oven."""
        try:
            self.__device = modbus.Instrument(self.__port, 1, close_port_after_each_call=True)
            connection_status = ConnectionStatus.CONNECTED
        except Exception:
            connection_status = ConnectionStatus.DISCONNECTED
        self.update_connection_status(connection_status)

    def update_port(self, port: str):
        """Updates the oven's connection port."""
        self.__port = port
        self.connect()

    def start(self):
        """
        Start the oven's connection timer, which handles maintaining a connection to the physical
        instrument.
        """
        self.connection_timer.start()


@dataclass
class InstrumentSet:
    """Container for instruments (ovens, potentiostats, etc.)"""

    oven: Union[Oven, "DeveloperOven"]
    potentiostat: None
