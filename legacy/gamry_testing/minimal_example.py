import math
from typing import Any

from comtypes import client  # type: ignore
from impedance_reader import ImpedanceReader

GamryCOM = client.GetModule("C:/Program Files (x86)/Gamry Instruments/Framework/GamryCom.exe")


# --------------------------------------------------------------------------------------------------
# functions
def init_pstat(potentiostat: Any, dc_voltage_vs_reference: float):
    # almost entirely copied from Potentiostatic EIS.exp

    # I turn this on early because it doesn't seem to matter if it's off?
    potentiostat.SetCell(GamryCOM.CellOn)
    potentiostat.SetCtrlMode(GamryCOM.PstatMode)
    potentiostat.SetAchSelect(GamryCOM.GND)
    potentiostat.SetIEStability(GamryCOM.StabilityFast)
    potentiostat.SetCASpeed(3)
    potentiostat.SetSenseSpeedMode(True)
    potentiostat.SetGround(GamryCOM.Float)
    potentiostat.SetIchRange(3.0)
    potentiostat.SetIchRangeMode(False)
    potentiostat.SetIchFilter(2.5)
    potentiostat.SetVchRange(3.0)
    potentiostat.SetVchRangeMode(False)

    potentiostat.SetIchOffsetEnable(True)
    potentiostat.SetVchOffsetEnable(True)

    potentiostat.SetVchFilter(2.5)
    potentiostat.SetAchRange(3.0)
    potentiostat.SetIERangeLowerLimit(0)
    potentiostat.SetIERange(0.03)
    potentiostat.SetIERangeMode(False)
    potentiostat.SetAnalogOut(0.0)
    potentiostat.SetVoltage(dc_voltage_vs_reference)
    potentiostat.SetPosFeedEnable(False)
    potentiostat.SetIruptMode(GamryCOM.IruptOff)


def init_readz(readz: Any, potentiostat: Any, impedance_guess: float):
    # copied from Potentiostatic EIS.exp
    readz.SetSpeed(GamryCOM.ReadZSpeedNorm)
    readz.SetGain(1.0)
    readz.SetINoise(0.0)
    readz.SetVNoise(0.0)
    readz.SetIENoise(0.0)
    readz.SetZmod(impedance_guess)
    readz.SetIdc(potentiostat.MeasureI())


# --------------------------------------------------------------------------------------------------
# values
INITIAL_FREQUENCY = 0.2
FINAL_FREQUENCY = 1000000
POINTS_PER_DECADE = 10
AC_VOLTAGE = 20 / 1000  # 20 mV. I assume that all voltages are in Volts, not millivolts
DC_VOLTAGE = 0
VS_OPEN_CIRCUIT_VOLTAGE = True
IMPEDANCE_GUESS = 1000

LOG_INCREMENT = 1 / POINTS_PER_DECADE
if INITIAL_FREQUENCY > FINAL_FREQUENCY:
    LOG_INCREMENT = -LOG_INCREMENT

MAXIMUM_MEASUREMENTS = math.ceil(
    abs(math.log10(FINAL_FREQUENCY) - math.log10(INITIAL_FREQUENCY)) * POINTS_PER_DECADE
)
# --------------------------------------------------------------------------------------------------
# create devices
device_list = client.CreateObject(GamryCOM.GamryDeviceList)
potentiostat = client.CreateObject(GamryCOM.GamryPC6Pstat)  # should this be GamryPstat instead?
potentiostat.Init(device_list.EnumSections()[0])  # grab first potentiostat
potentiostat.Open()
readz = client.CreateObject(GamryCOM.GamryReadZ)
readz.Init(potentiostat)
init_pstat(potentiostat, DC_VOLTAGE)
init_readz(readz, potentiostat, IMPEDANCE_GUESS)
impedance_reader = ImpedanceReader(
    readz, INITIAL_FREQUENCY, FINAL_FREQUENCY, AC_VOLTAGE, LOG_INCREMENT, MAXIMUM_MEASUREMENTS
)
impedance_reader.run()  # this actually measures and records data

# close and release items
potentiostat.SetCell(GamryCOM.CellOff)
potentiostat.Close()
device_list.Release()

print("Finished")

# TODO: test this script
# TODO: OPEN CIRCUIT VOLTAGE STUFF IF NEEDED
