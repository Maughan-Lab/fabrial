"""
This module acts as a wrapper around some GamryCOM items. If you want to understand it, I highly
recommend going through the example code for the Electrochemistry Toolkit.
"""

import json
import time
import types
from types import ModuleType
from typing import Any, Self

import comtypes.client as client  # type: ignore
from comtypes.client._events import _AdviseConnection  # type: ignore
from PyQt6.QtCore import QObject, pyqtSignal

from ..constants.paths import settings
from ..constants.paths.settings import gamry as Keys


class GamryInterface:
    """Convenience class for interacting with Gamry hardware."""

    def __init__(self) -> None:
        try:
            try:
                with open(settings.gamry.SAVED_SETTINGS_FILE, "r") as f:
                    gamry_data = json.load(f)
            except Exception:
                with open(settings.gamry.DEFAULT_SETTINGS_FILE, "r") as f:
                    gamry_data = json.load(f)
            self.valid: bool = gamry_data[Keys.ENABLED]
            if self.valid:
                gamry_location: str = gamry_data[Keys.LOCATION]
                self.GamryCOM = client.GetModule(gamry_location)
                self.device_list = client.CreateObject(self.GamryCOM.GamryDeviceList)
        except Exception:
            self.valid = False

    def is_valid(self) -> bool:
        """Whether the interface is valid. You should never use an invalid interface."""
        return self.valid

    def com_interface(self) -> types.ModuleType:
        """Get the COM interface used to communicate with GamryCOM."""
        return self.GamryCOM

    def get_pstat_list(self) -> list[str]:
        """Get a list of Gamry potentiostat identifiers."""
        return self.device_list.EnumSections()

    def cleanup(self):
        """Clean up the interface (call this before the application terminates)."""
        try:
            self.device_list.Release()  # closes GamryCOM.exe
        except Exception:
            pass


class Potentiostat:
    """
    Parameters
    ----------
    COM_interface
        The Module object used interface with Gamry.
    identifier
        An identifier for the physical potentiostat.
    """

    def __init__(self, COM_interface: types.ModuleType, identifer: str):
        self.GamryCOM = COM_interface
        self.id = identifer
        self.device = client.CreateObject(self.GamryCOM.GamryPC6Pstat)
        self.device.Init(self.id)

    def identifier(self) -> str:
        """Get the identifier for the potentiostat."""
        return self.id

    def inner(self) -> Any:
        """Access the underlying COM object this potentiostat uses."""
        return self.device

    def com_interface(self) -> ModuleType:
        """Access the potentiostat's underlying COM interface."""
        return self.GamryCOM

    def cleanup(self):
        """Clean up the potentiostat resources."""
        self.close()

    def initialize(self, dc_voltage_vs_reference: float) -> Self:
        """
        Initialize the potentiostat the same way Gamry does for the Potentiostatic EIS experiment.
        """
        # I know it's ugly, I'm sorry my child
        self.turn_on()
        self.device.SetCtrlMode(self.GamryCOM.PstatMode)
        self.device.SetAchSelect(self.GamryCOM.GND)
        self.device.SetIEStability(self.GamryCOM.StabilityFast)
        self.device.SetCASpeed(3)
        self.device.SetSenseSpeedMode(True)
        self.device.SetGround(self.GamryCOM.Float)
        self.device.SetIchRange(3.0)
        self.device.SetIchRangeMode(False)
        self.device.SetIchFilter(2.5)
        self.device.SetVchRange(3.0)
        self.device.SetVchRangeMode(False)

        self.device.SetIchOffsetEnable(True)
        self.device.SetVchOffsetEnable(True)

        self.device.SetVchFilter(2.5)
        self.device.SetAchRange(3.0)
        self.device.SetIERangeLowerLimit(0)
        self.device.SetIERange(0.03)
        self.device.SetIERangeMode(False)
        self.device.SetAnalogOut(0.0)
        self.device.SetVoltage(dc_voltage_vs_reference)
        self.device.SetPosFeedEnable(False)
        self.device.SetIruptMode(self.GamryCOM.IruptOff)

        return self

    def upper_frequency_limit(self) -> float:
        """Get the upper limit for the potentiostat's frequency."""
        return self.device.FreqLimitUpper()

    def lower_frequency_limit(self) -> float:
        """Get the lower limit for the potentiostat's frequency."""
        return self.device.FreqLimitLower()

    def clamp_frequency(self, frequency: float):
        """
        Clamp the input frequency to be between the upper and lower limit for the potentiostat,
        then return the resulting frequency.
        """
        lower_limit = self.lower_frequency_limit()
        upper_limit = self.upper_frequency_limit()
        if frequency > upper_limit:
            return upper_limit
        elif frequency < lower_limit:
            return lower_limit
        return frequency

    def open(self) -> Self:
        """
        Open to potentiostat for taking measurements. This must eventually be followed by a call to
        `close()`.
        """
        self.device.Open()
        return self

    def close(self) -> Self:
        """Close the potentiostat. You cannot take measurements after calling this function."""
        self.turn_off()
        time.sleep(0.5)  # necessary to make sure the potentiostat actually turns off
        self.device.Close()
        return self

    def turn_on(self) -> Self:
        """Turn the cell on."""
        self.device.SetCell(self.GamryCOM.CellOn)
        return self

    def turn_off(self) -> Self:
        """Turn the cell off."""
        self.device.SetCell(self.GamryCOM.CellOff)
        return self

    def measure_open_circuit_voltage(self) -> float:
        """Measure the open-circuit voltage."""
        voltage_reader = OCVoltageReader(self)
        return voltage_reader.run()

    # ----------------------------------------------------------------------------------------------
    # context manager
    def __enter__(self) -> Self:
        self.open()
        return self

    def __exit__(self, *exc_args):
        self.cleanup()


class ImpedanceReader(QObject):
    """
    Uses a `Potentiostat` to measure electrical impedance. This is synonymous to Gamry's
    `ReadZ`.
    """

    dataReady = pyqtSignal(bool)
    """
    Fires sometime after a call to `measure()` when the impedance reader has data ready. Sends:
    - Whether the measurement was successful as a `bool`.
    """

    def __init__(self, potentiostat: Potentiostat):
        QObject.__init__(self)
        self.pstat = potentiostat
        # stands for Read Z (Z = impedance)
        self.readz = client.CreateObject(self.pstat.com_interface().GamryReadZ)
        self.readz.Init(self.pstat.inner())
        self.connection = client.GetEvents(self.readz, self)

    def initialize(self, impedance_guess: float, speed_option: int) -> Self:
        """Initialize the reader the same way Gamry does in the Potentiostatic EIS experiment."""
        self.readz.SetSpeed(speed_option)
        self.readz.SetGain(1.0)
        self.readz.SetINoise(0.0)
        self.readz.SetVNoise(0.0)
        self.readz.SetIENoise(0.0)
        self.readz.SetZmod(impedance_guess)
        self.readz.SetIdc(self.pstat.inner().MeasureI())
        return self

    def measure(self, frequency: float, ac_voltage: float):
        """
        Perform a measurement. The reader will emit `dataReady` when data is ready to be read.

        Parameters
        ----------
        frequency
            The frequency to measure at (in Hz). This frequency is clamped to the potentiostats
            limits.
        ac_voltage
            The AC voltage to measure at (in V).
        """
        self.readz.Measure(self.pstat.clamp_frequency(frequency), ac_voltage)

    def cleanup(self):
        """Clean up the reader resources."""
        self.connection.disconnect()
        del self.connection

    def potentiostat(self) -> Potentiostat:
        """Access the potentiostat this reader is using."""
        return self.pstat

    def com_connection(self) -> _AdviseConnection:
        """Get the `comtypes` connection used to send events to the reader."""
        return self.connection

    # ----------------------------------------------------------------------------------------------
    # measurement values
    def frequency(self) -> float:
        """Get the current frequency in Hz."""
        return self.readz.Zfreq()

    def real_impedance(self) -> float:
        """Get the real part of the current impedance in Ohms."""
        return self.readz.Zreal()

    def imaginary_impedance(self) -> float:
        """Get the imaginary part of the current impedance in Ohms."""
        return self.readz.Zimag()

    def impedance_standard_deviation(self) -> float:
        """Get the current impedance standard deviation. This is also called Zsig."""
        return self.readz.Zsig()

    def impedance_magnitude(self) -> float:
        """Get the magnitude of the current impedance in Ohms. This is also called Zmod."""
        return self.readz.Zmod()

    def impedance_phase(self) -> float:
        """Get the phase of the current impedance in degrees."""
        return self.readz.Zphz()

    def dc_current(self) -> float:
        """Get the current DC current in Amps."""
        return self.readz.Idc()

    def dc_voltage(self) -> float:
        """Get the current DC voltage in Volts."""
        return self.readz.Vdc()

    def ie_range(self) -> float:
        """Get the current IE range (also called current range)."""
        return self.readz.IERange()

    # ----------------------------------------------------------------------------------------------
    # COM functions
    def _IGamryReadZEvents_OnDataDone(self, this: Any, error_status: bool):
        """
        This is a callback called by the `comtypes` module when the a potentiostat has completed a
        measurement.
        """
        self.dataReady.emit(error_status == 0)  # 0 indicates success

    def _IGamryReadZEvents_OnDataAvailable(self, this: Any):
        """Another callback that the application does not use right now."""
        pass

    # ----------------------------------------------------------------------------------------------
    # context manager
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_args):
        self.cleanup()


class OCVoltageReader:
    """Uses a `Potentiostat` to measure the open-circuit voltage."""

    SAMPLE_TIME = 0.25  # seconds

    def __init__(self, potentiostat: Potentiostat):
        self.pstat = potentiostat
        gamry_pstat = self.pstat.inner()
        self.GamryCOM = self.pstat.com_interface()
        self.signal = client.CreateObject(self.GamryCOM.GamrySignalConst)
        self.oc_reader = client.CreateObject(self.GamryCOM.GamryDtaqOcv)
        self.signal.Init(gamry_pstat, 0, 1, self.SAMPLE_TIME, self.GamryCOM.PstatMode)
        self.oc_reader.Init(gamry_pstat)

        self.finished = False
        self.open_circuit_voltage = 0.0

    def inner(self) -> Any:
        """Get the underlying COM object used to read the open-circuit voltage."""
        return self.oc_reader

    def run(self) -> float:
        """
        Run the open-circuit voltage test. This turns the cell off.

        Returns
        -------
        The open-circuit voltage in Volts.
        """
        # a lot of this code is probably redundant, but I'm copying from the Common Functions.exp
        # file (OCDelay)
        gamry_pstat = self.pstat.inner()
        gamry_pstat.SetCell(self.GamryCOM.CellOff)
        gamry_pstat.SetCtrlMode(self.GamryCOM.PstatMode)

        gamry_pstat.SetSenseSpeedMode(True)
        gamry_pstat.SetIConvention(self.GamryCOM.Anodic)
        gamry_pstat.SetGround(self.GamryCOM.Float)
        gamry_pstat.SetIchRange(3.0)
        gamry_pstat.SetIchRangeMode(True)
        gamry_pstat.SetIchOffsetEnable(False)
        gamry_pstat.SetIchFilter(1.0 / self.SAMPLE_TIME)
        gamry_pstat.SetVchRange(10.0)
        gamry_pstat.SetVchRangeMode(True)
        gamry_pstat.SetVchOffsetEnable(False)
        gamry_pstat.SetVchFilter(1.0 / self.SAMPLE_TIME)
        gamry_pstat.SetAchRange(3.0)
        gamry_pstat.SetIERange(0.03)
        gamry_pstat.SetIERangeMode(False)
        gamry_pstat.SetAnalogOut(0.0)
        gamry_pstat.SetVoltage(0.0)
        gamry_pstat.SetPosFeedEnable(False)
        gamry_pstat.SetIruptMode(self.GamryCOM.IruptOff)

        gamry_pstat.SetSignal(self.signal)
        gamry_pstat.InitSignal()

        gamry_pstat.FindVchRange()

        # actually run the open-circuit voltage test
        connection = client.GetEvents(self.oc_reader, self)
        self.oc_reader.Run(True)
        while not self.finished:
            client.PumpEvents(0.1)
        connection.disconnect()
        del connection

        return self.open_circuit_voltage  # return the last measured open-circuit voltage

    # ----------------------------------------------------------------------------------------------
    # COM functions
    def _IGamryDtaqEvents_OnDataAvailable(self, this) -> None:
        """Called whenever there are new open circuit voltage measurements."""
        points: list[list[float]] = self.oc_reader.Cook(1024)[1]
        self.open_circuit_voltage = points[1][-1]  # Vf

    def _IGamryDtaqEvents_OnDataDone(self, this):
        """Gets called when the timeout is reached."""
        self.finished = True


GAMRY = GamryInterface()
