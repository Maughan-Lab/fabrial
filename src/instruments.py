from dataclasses import dataclass
from enum import Enum
import json
from PyQt6.QtCore import pyqtSignal, QObject, QMutex
import minimalmodbus as modbus  # type: ignore
from .classes.mutex import SignalMutex
from typing import Union, TYPE_CHECKING
from .utility.timers import Timer
from . import Files

if TYPE_CHECKING:
    from developer import DeveloperOven


# TODO: this does not belong here
def to_str(connected: bool) -> str:
    """Convert a bool representing the connection status to text."""
    if connected:
        return "CONNECTED"
    else:
        return "DISCONNECTED"


# TODO: this does not belong here
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

    def get_lock(self) -> SignalMutex:
        """Access the lock."""
        return self.lock

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
        """Get the connection status of this instrument as a **bool**."""
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

    class ClampResult(Enum):
        """Result enum used by the `clamp_setpoint()` method."""

        NO_CLAMP = 0
        """No clamping occurred."""
        MAX_CLAMP = 1
        """The setpoint was clamped to the maximum oven temperature."""
        MIN_CLAMP = 2
        """The setpoint was clamped to the minimum oven temperature."""

    def __init__(self, oven_port: str = ""):
        super().__init__()
        self.port = oven_port
        # initialize the oven settings
        self.max_temperature: float
        self.min_temperature: float
        self.setpoint_register: int
        self.temperature_register: int
        self.number_of_decimals: int
        self.load_settings()
        # timers for connection and reading the temperature and setpoint
        self.temperature_timer = Timer(self, 1000, self.read_temp)
        self.setpoint_timer = Timer(self, 1000, self.get_setpoint)
        self.connection_timer = Timer(self, 1000, self.connect)
        self.connectionChanged.connect(self.handle_connection_change)

    def maximum_temperature(self):
        """Get the oven's maximum allowed temperature."""
        return self.max_temperature

    def minimum_temperature(self):
        """Get the oven's minimum allowed temperature."""
        return self.min_temperature

    def load_settings(self):
        """Load the oven's settings from the oven settings file."""
        with open(Files.Oven.SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        self.max_temperature = settings[Files.Oven.MAX_TEMPERATURE]
        self.min_temperature = settings[Files.Oven.MIN_TEMPERATURE]
        self.setpoint_register = settings[Files.Oven.SETPOINT_REGISTER]
        self.temperature_register = settings[Files.Oven.TEMPERATURE_REGISTER]
        self.number_of_decimals = settings[Files.Oven.NUM_DECIMALS]

    def save_settings(self):
        """Save the oven settings to the oven settings file."""
        settings = {
            Files.Oven.MAX_TEMPERATURE: self.max_temperature,
            Files.Oven.MIN_TEMPERATURE: self.min_temperature,
            Files.Oven.SETPOINT_REGISTER: self.setpoint_register,
            Files.Oven.TEMPERATURE_REGISTER: self.temperature_register,
            Files.Oven.NUM_DECIMALS: self.number_of_decimals,
        }
        with open(Files.Oven.SETTINGS_FILE, "w") as f:
            json.dump(settings, f)

    def handle_connection_change(self, connected: bool):
        if connected:
            self.connection_timer.stop()
            self.temperature_timer.start()
            self.setpoint_timer.start()
        else:
            self.temperature_timer.stop()
            self.setpoint_timer.stop()
            self.connection_timer.start()

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if on a successful read, None otherwise."""
        if not self.try_device_lock():
            return None

        temperature: float | None = None
        try:
            temperature = float(
                self.device.read_register(self.temperature_register, self.number_of_decimals)
            )
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
        False otherwise. If the provided setpoint is outside the oven's setpoint range, it is
        clamped.
        """
        if not self.try_device_lock():
            return False

        success = False
        try:
            self.device.write_register(
                self.setpoint_register, self.clamp_setpoint(setpoint)[0], self.number_of_decimals
            )
            self.setpointChanged.emit(setpoint)
            success = True
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        finally:
            self.device_lock.unlock()

        return success

    def get_setpoint(self) -> float | None:
        """Get the oven's setpoint. Returns **None** if the read fails."""
        if not self.try_device_lock():
            return None

        setpoint: float | None = None
        try:
            setpoint = float(
                self.device.read_register(self.setpoint_register, self.number_of_decimals)
            )
        except Exception:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        finally:
            self.device_lock.unlock()
        return setpoint

    def clamp_setpoint(self, setpoint: float) -> tuple[float, ClampResult]:
        """Clamp the provided **setpoint** to be within the oven's physical limits."""
        if setpoint > self.max_temperature:
            return (self.max_temperature, Oven.ClampResult.MAX_CLAMP)
        elif setpoint < self.min_temperature:
            return (self.min_temperature, Oven.ClampResult.MIN_CLAMP)
        return (setpoint, Oven.ClampResult.NO_CLAMP)

    def try_device_lock(self) -> bool:
        """Try to acquire the device lock with a timeout of 10 ms."""
        if self.device_lock.tryLock(10):
            return True
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


global INSTRUMENTS
INSTRUMENTS = InstrumentSet(Oven(), None)
