from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import pyqtSignal, QObject, QMutex
import minimalmodbus as modbus  # type: ignore
from classes.mutex import SignalMutex
from typing import Union, TYPE_CHECKING
from utility.timers import Timer
import time

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
        self.connection_status = ConnectionStatus.NULL

        # this lock indicates to the rest of the application the instrument is not available
        self.lock = SignalMutex()  # do not manually access the lock ever
        self.lockChanged = self.lock.lockChanged  # shortcut to signal inside self.lock

        # this lock ensures accessing the physical device is thread safe
        self.device_lock = QMutex()

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
        if self.connection_status != connection_status:
            self.connection_status = connection_status
            self.connectionChanged.emit(self.is_connected())

    def is_connected(self) -> bool:
        """Get the connection status of this instrument as a bool."""
        return bool(self.connection_status)

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
        self.port = oven_port
        self.temperature: float = -1
        self.setpoint: float = -1

        self.temperature_timer = Timer(self, 1000, self.read_temp)
        self.setpoint_timer = Timer(self, 1000, self.get_setpoint)

        self.connection_timer = Timer(self, 1000, self.connect)
        self.connectionChanged.connect(self.handle_connection_change)

    def handle_connection_change(self, connected: bool):
        if connected:
            self.connection_timer.stop()
            self.temperature_timer.start()
            self.setpoint_timer.start()
        else:
            self.temperature_timer.stop()
            self.setpoint_timer.stop()
            self.temperature = -1
            self.setpoint = -1
            self.connection_timer.start()

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if on a successful read, None otherwise."""
        if not self.try_device_lock():
            return None

        temperature: float | None = None
        try:
            temperature = float(
                self.device.read_register(self.TEMPERATURE_REGISTER, self.NUMBER_OF_DECIMALS)
            )
            if temperature != self.temperature:
                self.temperature = temperature
                self.temperatureChanged.emit(temperature)
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
            return None
        finally:
            self.device_lock.unlock()

        return temperature

    def change_setpoint(self, setpoint: float) -> bool:
        """
        Sets the oven's temperature to **setpoint**. Returns True if the operation was successful,
        False otherwise.
        """
        if not self.try_device_lock():
            return False

        success = False
        try:
            self.device.write_register(self.SETPOINT_REGISTER, setpoint, self.NUMBER_OF_DECIMALS)
            self.setpoint = setpoint
            self.setpointChanged.emit(setpoint)
            success = True
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        finally:
            self.device_lock.unlock()

        return success

    def get_setpoint(self) -> float | None:
        """Updates the oven's setpoint if on a successful read."""
        if not self.try_device_lock():
            return None

        setpoint: float | None = None
        try:
            setpoint = float(
                self.device.read_register(self.SETPOINT_REGISTER, self.NUMBER_OF_DECIMALS)
            )
            if setpoint != self.setpoint:
                self.setpoint = setpoint
                self.setpointChanged.emit(setpoint)
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        finally:
            self.device_lock.unlock()
        return setpoint

    def try_device_lock(self) -> bool:
        """Try to acquire the device lock twice, pausing in between."""
        for i in range(2):
            if self.device_lock.tryLock():
                return True
            if i != 1:
                time.sleep(0.01)
        return False

    def connect(self):
        """Attempts to connect to the oven."""
        try:
            self.device = modbus.Instrument(self.port, 1, close_port_after_each_call=True)
            connection_status = ConnectionStatus.CONNECTED
        except Exception:
            connection_status = ConnectionStatus.DISCONNECTED
        self.update_connection_status(connection_status)

    def update_port(self, port: str):
        """Updates the oven's connection port."""
        self.port = port
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
