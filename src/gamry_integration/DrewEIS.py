import time
from math import log10
import comtypes.client as client
from .EventHandler import ReadZEventHandler
from io import TextIOWrapper

GamryCOM = client.GetModule(r"C:\Program Files (x86)\Gamry Instruments\Framework\GamryCom.exe")


class GamryCOMError(Exception):
    pass


def initializepstat(pstat, dc: float):
    pstat.SetCtrlMode(GamryCOM.PstatMode)
    pstat.SetCell(GamryCOM.CellOff)
    pstat.SetIEStability(GamryCOM.StabilityFast)
    pstat.SetVoltage(dc)


# determines number of data points to be taken based on frequency range and points per decade setup parameters
# DREW: try to understand this
# DREW: it's a bookkeeping thing to calculate how long to run measurements for
def eispoints(final_freq: float, initial_freq: float, ptsperdec: int):
    return round(0.5 + (abs(log10(final_freq) - log10(initial_freq)) * ptsperdec))


def writeheader(datafile: TextIOWrapper):
    datafile.write(
        "EXPLAIN\n"
        "TAG\tEISPOT\n"
        "TITLE\tLABEL\tPotentiostatic EIS\tTest &Identifier\n"
        "ZCURVE\tTABLE\n"
        "\tPt\tTime\tFreq\tZreal\tZimag\tZsig\tZmod\tZphz\tIdc\tVdc\tIERange\n"
        "\t#\ts\tHz\tohm\tohm\tV\tohm\t°\tA\tV\t#\n"
    )


# run here
# events from GamryCom are pumped back every second while data acquisition is active
def main():
    initfreq = 2000000  # initial frequency to run
    finfreq = 0.2  # run to this frequency
    ac = 0.02  # AC voltage, in Volts
    dc = 0.0  # dc voltage, in Volts
    # DREW: ptsperdec = points per decade
    ptsperdec = 10  # amount of data points to take per decade of frequency

    maxpoints = eispoints(finfreq, initfreq, ptsperdec)

    loginc = 1 / (ptsperdec)
    # DREW: if we are doing a high-frequency to low-frequency sweep, make a change
    if initfreq > finfreq:
        loginc = -loginc

    # initialize the file
    file = open("Open Air Test (Drew Software).DTA", "w")
    writeheader(file)

    # gets the initial status (???), so probably not super important
    status1 = GamryCOM.gcREADZSTATUS

    # initialize the pstat
    pstat = client.CreateObject(GamryCOM.GamryPstat)
    devices = client.CreateObject(GamryCOM.GamryDeviceList)
    print(devices.EnumSections())
    pstat.Init(devices.EnumSections()[0])  # grab first pstat
    pstat.Open()
    initializepstat(pstat, dc)

    # initialize the readz
    readz = client.CreateObject("GamryCOM.GamryReadZ")
    readz.Init(pstat)
    readz.SetZmod(180000)  # set the initial guess to 180000 ohms

    dtaqsink = ReadZEventHandler(readz, pstat, file, maxpoints, loginc, initfreq, ac)
    connection = client.GetEvents(readz, dtaqsink)

    pstat.SetCell(GamryCOM.CellOn)

    active = True

    starttime = 0

    readz.Measure(initfreq, ac)

    # DREW: this is the mainloop, but it supports time.sleep, so you can probably integrate this
    # without multiprocessing and just use threads instead
    print("mainlooping")
    count = 1
    while active is True:
        # DREW: look at the docs in Program Files for why this function takes input `1`
        print(count)
        client.PumpEvents(1)
        time.sleep(0.1)
        count += 1
        # NOTE: you will have to run Gamry in a separate process. Data collection takes too long for
        # Quincy to remain response. You can run multiple potentiostats in one process, though.


if __name__ == "__main__":
    main()
