from dataclasses import dataclass
from enum import Enum
import json
from PyQt6.QtCore import pyqtSignal, QObject, QMutex, QMutexLocker
import minimalmodbus as modbus  # type: ignore
from .classes.lock import DataMutex
from typing import Union, TYPE_CHECKING
from .utility.timers import Timer
from .enums.status import ConnectionStatus
from . import Files

if TYPE_CHECKING:
    from developer import DeveloperOven


class Instrument(QObject):
    """
    Abstract class to represent instruments. When using methods that change the physical oven,
    call acquire() followed at some point by release().
    """

    # signals
    connectionChanged = pyqtSignal(bool)
    """
    Fires whenever the connection status changes. Sends whether the instrument is connected as a
    **bool**.
    """
    lockChanged = pyqtSignal(bool)
    """
    Fires whenever the instrument is locked/unlocked. Sends whether the instrument is unlocked as a
    **bool**.
    """

    def __init__(self):
        super().__init__()
        self.connection_status = ConnectionStatus.NULL

        # this lock system indicates to the rest of the application whether the instrument is
        # available
        self.unlocked = True
        # this lock ensures accessing the physical device is thread safe
        self.physical_device_lock = QMutex()

    def lock(self):
        """
        Make the instrument available for only one process. This should be followed by a call to
        **unlock()**. Emits signals.
        """
        self.unlocked = False
        self.lockChanged.emit(False)

    def unlock(self):
        """Make the instrument available for other processes. Emits signals."""
        self.unlocked = True
        self.lockChanged.emit(True)

    def is_unlocked(self) -> bool:
        """Whether the instrument is available."""
        return self.unlocked

    def device_lock(self) -> QMutex:
        """Get the device lock, which ensures accessing the physical device is thread safe."""
        return self.physical_device_lock

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


class InstrumentLocker[InstrumentType: Instrument]:  # generic
    """Locks and unlocks an instrument using the context manager."""

    def __init__(self, instrument: InstrumentType):
        self.instrument = instrument

    def __enter__(self) -> InstrumentType:
        self.instrument.lock()
        return self.instrument

    def __exit__(self, *exception_info):
        # we don't care about exceptions here
        self.instrument.unlock()


class Oven(Instrument):
    """
    Class to represent the physical oven the application controls. Once `start()` is called, the
    oven will attempt to connect automatically and will also run a stability check.
    """

    # signals
    temperatureChanged = pyqtSignal(float)
    """Fires whenever the oven's temperature *changes*. Sends the temperature as a **float**."""
    setpointChanged = pyqtSignal(float)
    """Fires whenever the oven's setpoint *changes*. Sends the setpoint as a **float**."""
    stabilityChanged = pyqtSignal(bool)
    """
    Fires whenever the oven's stability status changes. Sends a **bool** indicating whether the
    temperature is stable.
    """
    stabilityCountChanged = pyqtSignal(int)
    """
    Fires whenever the oven's stability measurement count changes. Sends the new count as an
    **int**.
    """

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
        self.stability_tolerance: float
        self.minimum_stability_measurements: int
        self.load_settings()
        # do not access these directly
        self.last_temperature: float | None = None
        self.last_setpoint: float | None = None
        self.stability_measurement_count = 0
        self.stable = DataMutex(False)
        self.disconnected_count = 0
        # timers for connection and reading the temperature and setpoint
        self.temperature_timer = Timer(self, 1000, self.read_temp)
        self.setpoint_timer = Timer(self, 1000, self.get_setpoint)
        self.stability_timer = Timer(self, 50, self.check_stability)
        self.connection_timer = Timer(self, 1000, self.connect)
        self.connectionChanged.connect(self.handle_connection_change)

    def maximum_temperature(self) -> float:
        """Get the oven's maximum allowed temperature."""
        return self.max_temperature

    def minimum_temperature(self) -> float:
        """Get the oven's minimum allowed temperature."""
        return self.min_temperature

    def minimum_measurements(self) -> int:
        """Get the oven's minimum number of measurements for stability."""
        return self.minimum_stability_measurements

    def load_settings(self):
        """Load the oven's settings from the oven settings file."""
        with open(Files.Oven.SETTINGS_FILE, "r") as f:
            settings = json.load(f)
        self.max_temperature = settings[Files.Oven.MAX_TEMPERATURE]
        self.min_temperature = settings[Files.Oven.MIN_TEMPERATURE]
        self.setpoint_register = settings[Files.Oven.SETPOINT_REGISTER]
        self.temperature_register = settings[Files.Oven.TEMPERATURE_REGISTER]
        self.number_of_decimals = settings[Files.Oven.NUM_DECIMALS]
        self.stability_tolerance = settings[Files.Oven.STABILITY_TOLERANCE]
        self.minimum_stability_measurements = settings[Files.Oven.MINIMUM_STABILITY_MEASUREMENTS]

    def save_settings(self):
        """Save the oven settings to the oven settings file."""
        settings = {
            Files.Oven.MAX_TEMPERATURE: self.max_temperature,
            Files.Oven.MIN_TEMPERATURE: self.min_temperature,
            Files.Oven.SETPOINT_REGISTER: self.setpoint_register,
            Files.Oven.TEMPERATURE_REGISTER: self.temperature_register,
            Files.Oven.NUM_DECIMALS: self.number_of_decimals,
            Files.Oven.STABILITY_TOLERANCE: self.stability_tolerance,
            Files.Oven.MINIMUM_STABILITY_MEASUREMENTS: self.minimum_stability_measurements,
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
            self.last_temperature = None
            self.last_setpoint = None
            self.connection_timer.start()

    def read_temp(self) -> float | None:
        """
        Returns the oven's temperature if on a successful read, **None** otherwise. This is
        thread-safe.
        """
        with QMutexLocker(self.device_lock()):
            try:
                temperature = float(
                    self.device.read_register(self.temperature_register, self.number_of_decimals)
                )
                self.update_temperature(temperature)
                return temperature
            except Exception:
                self.update_connection_status(ConnectionStatus.DISCONNECTED)
                return None

    def change_setpoint(self, setpoint: float) -> bool:
        """
        Sets the oven's temperature to **setpoint**. Returns **True** if the operation was
        successful, **False** otherwise. If the provided setpoint is outside the oven's setpoint
        range, it is clamped. This reset's the oven's stability. This is thread-safe.
        """
        with QMutexLocker(self.device_lock()):
            try:
                self.device.write_register(
                    self.setpoint_register,
                    self.clamp_setpoint(setpoint)[0],
                    self.number_of_decimals,
                )
                self.update_setpoint(setpoint)
                self.reset_stability()
                return True
            except Exception:
                self.update_connection_status(ConnectionStatus.DISCONNECTED)
                return False

    def get_setpoint(self) -> float | None:
        """Get the oven's setpoint. Returns **None** if the read fails. This is thread-safe."""
        with QMutexLocker(self.device_lock()):
            try:
                setpoint = float(
                    self.device.read_register(self.setpoint_register, self.number_of_decimals)
                )
                self.update_setpoint(setpoint)
                return setpoint
            except Exception:
                self.update_connection_status(ConnectionStatus.DISCONNECTED)
                return None

    def update_temperature(self, temperature: float):
        """Update the last temperature and emit signals on a change. This method is private."""
        if self.last_temperature is None or self.last_temperature != temperature:
            self.last_temperature = temperature
            self.temperatureChanged.emit(temperature)

    def update_setpoint(self, setpoint: float):
        """Update the last setpoint and emit signals on a change. This method is private."""
        if self.last_setpoint is None or self.last_setpoint != setpoint:
            self.last_setpoint = setpoint
            self.setpointChanged.emit(setpoint)

    def clamp_setpoint(self, setpoint: float) -> tuple[float, ClampResult]:
        """Clamp the provided **setpoint** to be within the oven's physical limits."""
        if setpoint > self.max_temperature:
            return (self.max_temperature, Oven.ClampResult.MAX_CLAMP)
        elif setpoint < self.min_temperature:
            return (self.min_temperature, Oven.ClampResult.MIN_CLAMP)
        return (setpoint, Oven.ClampResult.NO_CLAMP)

    def connect(self):
        """Attempts to connect to the oven. This is thread-safe."""
        with QMutexLocker(self.device_lock()):
            try:
                self.device = modbus.Instrument(self.port, 1, close_port_after_each_call=True)
                connection_status = ConnectionStatus.CONNECTED
            except Exception:
                connection_status = ConnectionStatus.DISCONNECTED
            self.update_connection_status(connection_status)

    def check_stability(self):
        """Check whether the oven's temperature is stable."""
        MAX_DICONNECTS = 10

        if not self.is_connected():
            # if we're not connected for MAX_DISCONNECTS stability checks, we are unstable
            self.disconnected_count += 1
            if self.disconnected_count == MAX_DICONNECTS:  # arbitrary value
                self.reset_stability()
            elif self.disconnected_count > MAX_DICONNECTS:
                self.disconnected_count == MAX_DICONNECTS + 1
        else:
            self.disconnected_count = 0
            # if there are values ready
            if self.last_temperature is not None and self.last_setpoint is not None:
                # if the last temperature measurement is within the stability tolerance
                if self.measurement_is_stable(self.last_temperature, self.last_setpoint):
                    # if we're not already stable, check to see if we can enter the stable state
                    if not self.is_stable():
                        self.increment_stability_count()

                        if self.stability_measurement_count >= self.minimum_stability_measurements:
                            self.update_stability_status(True)
                else:
                    # we're not stable, update accordingly
                    self.reset_stability()

    def update_stability_count(self, count: int):
        """Update the stability measurement count and emit signals on a change."""
        if self.stability_measurement_count != count:
            self.stability_measurement_count = count
            self.stabilityCountChanged.emit(count)

    def increment_stability_count(self):
        """Increment the stability measurement count by 1 and emit signals."""
        self.stability_measurement_count += 1
        self.stabilityCountChanged.emit(self.stability_measurement_count)

    def update_stability_status(self, stable: bool):
        """Update the oven's stability status and emit signals on a change."""
        if self.stable.get() != stable:
            self.stable.set(stable)
            self.stabilityChanged.emit(stable)

    def reset_stability(self):
        """Reset the oven's stability status and counter."""
        self.update_stability_count(0)
        self.update_stability_status(False)

    def is_stable(self) -> bool:
        """Whether the oven's temperature is stable. This is thread safe."""
        return self.stable.get()

    def stability_count(self) -> int:
        """Get the number of stability counts on the oven."""
        return self.stability_measurement_count

    def measurement_is_stable(self, temperature: float, setpoint: float) -> bool:
        """Whether the temperature is within the oven's stability tolerance."""
        return abs(temperature - setpoint) <= self.stability_tolerance

    def set_port(self, port: str):
        """
        Updates the oven's connection port. The oven automatically tries to reconnect. This is
        thread-safe.
        """
        self.port = port
        self.connect()

    def start(self):
        """
        Start the oven's connection timer, which handles maintaining a connection to the physical
        instrument.
        """
        self.connection_timer.start()
        self.stability_timer.start()


@dataclass
class InstrumentSet:
    """Container for instruments (ovens, potentiostats, etc.)"""

    oven: Union[Oven, "DeveloperOven"]
    potentiostat: None


global INSTRUMENTS
INSTRUMENTS = InstrumentSet(Oven(), None)
