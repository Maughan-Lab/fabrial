import json
import time
import types
from types import ModuleType
from typing import Any, Self

import comtypes.client as client  # type: ignore

from .. import Files


class GamryInterface:
    """Convenience class for interacting with Gamry hardware."""

    def __init__(self) -> None:
        Keys = Files.ApplicationSettings.Gamry
        try:
            with open(Files.ApplicationSettings.Gamry.SETTINGS_FILE, "r") as f:
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
        if self.valid:
            self.device_list.Release()  # closes GamryCOM.exe


class Potentiostat:
    def __init__(self, COM_interface: types.ModuleType, identifer: str):
        """
        :param COM_interface: The Module object used interface with Gamry.
        :param identifier: An identifier for the physical potentiostat.
        """
        self.GamryCOM = COM_interface
        self.id = identifer
        self.device = client.CreateObject(self.GamryCOM.GamryPstat)
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
        self.device.Release()

    def initialize(self, dc_voltage: float, impedance_guess: float) -> Self:
        """
        Initialize the potentiostat the same way Gamry does for the Potentiostatic EIS experiment.
        """
        # I know it's ugly, I'm sorry my child
        self.device.SetCell(self.GamryCOM.CellOn)
        self.device.InstrumentSpecificInitialize()
        self.device.SetAchSelect(self.GamryCOM.AchSelect_GND)
        self.device.SetCtrlMode(self.GamryCOM.PstatMode)
        self.device.SetStability(self.GamryCOM.StabilityFast)
        self.device.SetCASpeed(self.GamryCOM.CASpeedMedFast)
        self.device.SetSenseSpeedMode(True)
        self.device.SetConvention(self.GamryCOM.Anodic)
        self.device.SetGround(self.GamryCOM.Float)
        self.device.SetIchRange(3.0)
        self.device.SetIchRangeMode(False)  # might fail
        self.device.SetIchFilter(2.5)
        self.device.SetVchRange(3.0)
        self.device.SetVchRangeMode(False)

        self.device.SetIchOffsetEnable(True)
        self.device.SetVchOffsetEnable(True)

        self.device.SetVchFilter(2.5)
        self.device.SetAchRange(3.0)
        self.device.SetIERangeLowerLimit(None)  # might fail

        IE_range = self.device.TestIERange(dc_voltage / impedance_guess)
        self.device.SetIERange(IE_range)

        self.device.SetIERangeMode(False)
        self.device.SetAnalogOut(0.0)
        self.device.SetVoltage(dc_voltage)
        self.device.SetPosFeedEnable(False)  # might fail
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
        self.device.SetCell(self.GamryCOM.CellOff)
        time.sleep(1)  # necessary to make sure the potentiostat actually turns off
        self.device.Close()
        return self

    # ----------------------------------------------------------------------------------------------
    # context manager
    def __enter__(self) -> Self:
        self.open()
        return self

    def __exit__(self, *exc_args):
        self.close()
        self.cleanup()


class ImpedanceReader:
    """
    Uses a **Potentiostat** to measure electrical impedance. This is synonymous to Gamry's
    **ReadZ**.
    """

    def __init__(self, potentiostat: Potentiostat):
        self.pstat = potentiostat
        # stands for Read Z (Z = impedance)
        self.readz = client.CreateObject(self.pstat.com_interface().GamryReadZ)

    def initialize(self, impedance_guess: float) -> Self:
        """Initialize the reader the same way Gamry does in the Potentiostatic EIS experiment."""
        self.readz.SetGain(1.0)
        self.readz.SetINoise(0.0)
        self.readz.SetVNoise(0.0)
        self.readz.SetIENoise(0.0)
        self.readz.SetZmod(impedance_guess)
        self.readz.SetIdc(self.pstat.inner().MeasureI())
        return self

    def measure(self, frequency: float, ac_voltage: float) -> bool:
        """
        Perform a measurement.

        :param frequency: The frequency to measure at (in Hz).
        :param ac_voltage: The AC voltage to measure at (in V).

        :returns: Whether the measurement succeeded.
        """
        return self.readz.Measure(frequency, ac_voltage)

    def cleanup(self):
        """Clean up the reader resources."""
        self.readz.Release()

    def potentiostat(self) -> Potentiostat:
        """Access the potentiostat this reader is using."""
        return self.pstat

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
    # context manager
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_args):
        self.cleanup()


GAMRY = GamryInterface()
