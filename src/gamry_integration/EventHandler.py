import ctypes
import time
from io import TextIOWrapper
from math import log10

from comtypes import client

GamryCOM = client.GetModule(r"C:\Program Files (x86)\Gamry Instruments\Framework\GamryCom.exe")


def mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


# turn this into a QObject so you can use signals
class ReadZEventHandler(object):
    def __init__(
        self,
        dtaq: object,
        pstat: object,
        datafile: TextIOWrapper,
        maxpoints: int,
        log_increment: float,
        initial_frequency: float,
        ac: float,
    ):
        self.dtaq = dtaq
        self.pstat = pstat
        self.data = []
        self.file = datafile
        self.point = 0
        self.maxpoints = maxpoints
        self.log_increment = log_increment
        self.initial_frequency = initial_frequency
        self.freq = initial_frequency
        self.ac = ac

    def writedata(
        self,
        pt: float,
        time: float,
        freq: float,
        zreal: float,
        zimg: float,
        zsig: float,
        zmod: float,
        zphz: float,
        idc: float,
        vdc: float,
        ier: float,
    ):
        self.file.write(
            "\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n".format(
                pt, time, freq, zreal, zimg, zsig, zmod, zphz, idc, vdc, ier
            )
        )

    # unlike other experiments, cook gets the lissajous data points. Zmod, Zphz, etc must be collected after DataDone is fired
    def cook(self):
        count = 1
        while count > 0:
            count, points = self.dtaq.Cook(1024)
            self.data.extend(zip(*points))

    # cooks lissajous data points when DataAvalible event is fired
    def _IGamryReadZEvents_OnDataAvailable(self, this):
        self.cook()

    # DREW: it looks like this will get called whenever there is new data
    # DREW: yup that's correct, and the function name is so weird because that's how the interface defines it
    # The bread and butter of ReadZ. All readz.measure() is called from here after the very first frequency point
    # DREW: `this` is necessary because the C object passes itself
    def _IGamryReadZEvents_OnDataDone(self, this, status1):
        print(self.freq)
        # status = self.dtaq.StatusMessage()  # string based message about data point
        passes = 0

        datatime = time.process_time()

        # data acceptable, i.e. an impedance value was able to be obtained. Does not indicate quality
        if status1 == 0:

            self.writedata(
                self.point,
                datatime,
                self.dtaq.Zfreq(),
                self.dtaq.Zreal(),
                self.dtaq.Zimag(),
                self.dtaq.Zsig(),
                self.dtaq.Zmod(),
                self.dtaq.Zphz(),
                self.dtaq.Idc(),
                self.dtaq.Vdc(),
                self.dtaq.IERange(),
            )

            self.point += 1
            self.freq = 10 ** (log10(self.initial_frequency) + (self.point * self.log_increment))
            # we have acquired all data points over specified freq range. Clean up and exit
            if self.point > self.maxpoints:
                self.stop_acquisition()
                return
            else:  # still more data points to be collected. Measure impednace at next point
                self.dtaq.Measure(self.freq, self.ac)
                return
        # impedance value could not be determined. Retry 10 times and throw an error.
        # At each re-try the instrument makes automatic changes to try and get a value the next pass.
        # Give user an option to cancel experiment, retry point, or move to next point
        elif status1 == 1:
            if passes > 10:
                result1 = mbox(
                    "Measurement Error", "Unable to take measurement at {} Hz".format(self.freq), 6
                )
                if result1 == 2:  # abort
                    self.stop_acquisition()
                if result1 == 10:  # retry current frequency
                    passes = 0
                    self.dtaq.Measure(self.freq, self.ac)
                if result1 == 11:  # move to next frequency self.point
                    passes = 0
                    self.point = self.point + 1
                    self.freq = 10 ** (log10(self.initial_frequency) + (self.point * self.log_increment))
                    self.dtaq.Measure(self.freq, self.ac)
            else:
                passes = passes + 1
                self.dtaq.Measure(self.freq, self.ac)

        else:  # impedance value could not be determined. Catch all
            result = mbox("Measurement Error", "Bad Measurement at {} Hz".format(self.freq), 6)
            if result == 2:  # abort
                self.stop_acquisition()
            if result == 10:  # retry current frequency
                self.dtaq.Measure(self.freq, self.ac)
            if result == 11:  # move to next frequency self.point
                self.point = self.point + 1
                self.freq = 10 ** (log10(self.initial_frequency) + (self.point * self.log_increment))
                self.dtaq.Measure(self.freq, self.ac)

    def stop_acquisition(self):
        self.pstat.SetCell(GamryCOM.CellOff)
        time.sleep(1)
        self.pstat.Close()  # actually ends the COM connection
        self.file.close()
        print("done")
