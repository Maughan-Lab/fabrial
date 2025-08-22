import csv
import math
import time
from typing import Any

from comtypes import client  # type: ignore


class ImpedanceReader:
    def __init__(
        self,
        readz: Any,
        initial_frequency: float,
        final_frequency: float,
        ac_voltage: float,
        log_increment: float,
        maximum_measurements: int,
    ):
        self.readz = readz
        self.initial_frequency = initial_frequency
        self.final_frequency = final_frequency
        self.ac_voltage = ac_voltage
        self.log_increment = log_increment
        self.maximum_measurements = maximum_measurements

        self.measurement_count = 0
        self.calibration_measurement = True
        self.start_time = 0.0
        self.connection = client.GetEvents(self.readz, self)

        # create file and write headers
        self.file = open(
            "output.DTA",
            "w",
            1,  # line buffer
            newline="",  # necessary for CSVwriter
        )
        self.writer = csv.writer(self.file, delimiter="\t")
        self.writer.writerows(
            [
                ["EXPLAIN"],
                ["TAG", "EISPOT"],
                ["TITLE", "LABEL", "Potentiostatic EIS", "Test &Identifier"],
                [],
                ["ZCURVE", "TABLE"],
                [
                    "",
                    "Pt",
                    "Time",
                    "Freq",
                    "Zreal",
                    "Zimag",
                    "Zsig",
                    "Zmod",
                    "Zphz",
                    "Idc",
                    "Vdc",
                    "IERange",
                ],
                ["", "#", "s", "Hz", "ohm", "ohm", "V", "ohm", "°", "A", "V", "#"],
            ],
        )

    def run(self):
        self.start_time = time.time()
        # calibration measurement (triggers a chain of other measurements)
        self.readz.Measure(self.initial_frequency, self.ac_voltage)
        while not self.is_finished():
            client.PumpEvents(0.1)

        self.file.close()
        self.connection.disconnect()
        del self.connection

    def is_finished(self) -> bool:
        return self.measurement_count > self.maximum_measurements

    def record_measurement(self):
        self.writer.writerow(
            [
                "",  # for initial tab
                self.measurement_count,
            ]
            + [  # round all values to 6 decimal places
                round(value, 6)
                for value in [
                    time.time() - self.start_time,
                    self.frequency(),
                    self.real_impedance(),
                    self.imaginary_impedance(),
                    self.impedance_standard_deviation(),
                    self.impedance_magnitude(),
                    self.impedance_phase(),
                    self.dc_current(),
                    self.dc_voltage(),
                    self.ie_range(),
                ]
            ]
        )

    # ----------------------------------------------------------------------------------------------
    # COM functions
    def _IGamryReadZEvents_OnDataDone(self, this: Any, error_status: int):
        print(self.measurement_count)
        if error_status != 0:
            # in general ignoring the error status because it isn't relevant for this example
            print("An error occurred")

        # redo the first measurement once so the potentiostat is calibrated
        if self.calibration_measurement:
            self.calibration_measurement = False
            self.readz.Measure(self.initial_frequency, self.ac_voltage)
            return

        # if we got here we are actually measuring and recording data
        self.record_measurement()
        self.measurement_count += 1
        if not self.is_finished():
            desired_frequency = math.pow(
                10,
                math.log10(self.initial_frequency) + self.measurement_count * self.log_increment,
            )
            self.readz.Measure(desired_frequency, self.ac_voltage)
            return

    def _IGamryReadZEvents_OnDataAvailable(self, this: Any):
        # unused
        pass

    # ----------------------------------------------------------------------------------------------
    # measurement values
    def frequency(self) -> float:
        return self.readz.Zfreq()

    def real_impedance(self) -> float:
        return self.readz.Zreal()

    def imaginary_impedance(self) -> float:
        return self.readz.Zimag()

    def impedance_standard_deviation(self) -> float:
        return self.readz.Zsig()

    def impedance_magnitude(self) -> float:
        return self.readz.Zmod()

    def impedance_phase(self) -> float:
        return self.readz.Zphz()

    def dc_current(self) -> float:
        return self.readz.Idc()

    def dc_voltage(self) -> float:
        return self.readz.Vdc()

    def ie_range(self) -> float:
        return self.readz.IERange()
