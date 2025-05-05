import csv
import math
import os
import time
from contextlib import ExitStack
from io import TextIOWrapper
from typing import Any, Iterable

from PyQt6.QtWidgets import QMessageBox

from .....classes.process import AbstractGraphingProcess
from .....classes.runners import ProcessRunner
from .....gamry_integration.Gamry import GAMRY, ImpedanceReader, Potentiostat
from . import encoding
from .encoding import FileFormat, Filenames, Headers


class EISProcess(AbstractGraphingProcess):
    """Run a clone of the Gamry Potentiostatic EIS.exp file."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        super().__init__(runner, data, name)
        # unpack the dictionary values for easier access
        self.initial_frequency = data[encoding.INITIAL_FREQUENCY]
        self.final_frequency = data[encoding.FINAL_FREQUENCY]
        self.points_per_decade = data[encoding.POINTS_PER_DECADE]
        self.ac_voltage = data[encoding.AC_VOLTAGE] / 1000  # convert from mV to V
        self.dc_voltage = data[encoding.DC_voltage]
        self.area = data[encoding.AREA]
        self.impedance_guess = data[encoding.ESTIMATED_IMPEDANCE]
        self.pstat_identifiers = data[encoding.SELECTED_PSTATS]

    def run(self) -> None:
        # calculate the maximum number of measurements
        maximum_measurements = math.ceil(
            abs(math.log10(self.final_frequency) - math.log10(self.initial_frequency))
            * self.points_per_decade
        )
        # calculate the log increment
        log_increment = 1 / self.points_per_decade
        if self.initial_frequency > self.final_frequency:
            # if we are sweeping high frequency to low frequency, we need to decrease in frequency
            log_increment = -log_increment

        # open all potentiostats and impedance readers using a context manager so they get closed
        # automatically
        with ExitStack() as context_manager:
            pstats: list[Potentiostat] = []
            impedance_readers: list[ImpedanceReader] = []
            # create, open, and initialize the pstats and impedance readers
            for identifer in self.pstat_identifiers:
                potentiostat = Potentiostat(GAMRY.com_interface(), identifer)
                context_manager.enter_context(potentiostat)
                potentiostat.initialize(self.dc_voltage, self.impedance_guess)
                pstats.append(potentiostat)

                impedance_reader = ImpedanceReader(potentiostat)
                context_manager.enter_context(impedance_reader)
                impedance_reader.initialize(self.impedance_guess)
                impedance_readers.append(impedance_reader)

            # do the first measurement (I think to get the potentiostats ready)
            for impedance_reader in impedance_readers:
                impedance_reader.measure(self.initial_frequency, self.ac_voltage)

            # create the data files and put them in the context manager
            files = self.create_files(impedance_readers)
            for file in files.values():
                context_manager.enter_context(file)

            # measure and record data until we hit the measurement limit or get #canceled
            measurement_count = 0
            while measurement_count < maximum_measurements:
                desired_frequency = math.pow(
                    10, math.log10(self.initial_frequency) + measurement_count * log_increment
                )

                for impedance_reader in impedance_readers:
                    frequency = impedance_reader.potentiostat().clamp_frequency(desired_frequency)

                    success = impedance_reader.measure(frequency, self.ac_voltage)
                    while not success:
                        # if we failed to read, retry 10 times. If we still failed, ask the user
                        # what to do
                        retry_count = 0
                        while retry_count < 10:
                            success = impedance_reader.measure(frequency, self.ac_voltage)
                            if success:
                                break
                            retry_count += 1
                        if not success:
                            # show an error message and ask the user what to do
                            identifer = impedance_reader.potentiostat().identifier()
                            self.send_message(
                                f"Failed to take measurement for potentiostat {identifer} "
                                f"at frequency {frequency}. "
                                "Continue to next frequency, retry measurement, "
                                "or abort experiment?",
                                QMessageBox.StandardButton.Yes
                                | QMessageBox.StandardButton.Retry
                                | QMessageBox.StandardButton.Abort,
                            )
                            match self.wait_on_response():
                                case QMessageBox.StandardButton.Yes:
                                    break
                                case QMessageBox.StandardButton.Retry:
                                    continue
                                case QMessageBox.StandardButton.Abort:
                                    self.cancel()
                                    break

                    if self.is_canceled():
                        break
                    self.record_measurement(measurement_count, files, impedance_reader)

                measurement_count += 1
                if not self.wait(50):
                    break

    @staticmethod
    def directory_name():
        return "Electrochemical Impedance Spectroscopy"

    def create_files(
        self, readers: Iterable[ImpedanceReader]
    ) -> dict[ImpedanceReader, TextIOWrapper]:
        """
        Create the data files and their write headers.

        :param readers: The impedance readers being used by the process.
        :returns: A dictionary that corresponds **ImpedanceReader**s to their data file.
        """
        files_dict = dict()
        for impedance_reader in readers:
            identifier = impedance_reader.potentiostat().identifier()
            # file names are based on the potentiostat identifier
            file = open(
                os.path.join(self.directory(), Filenames.FILE_BASE.format(identifier)),
                "w",
                1,
                newline="",
            )
            csv.writer(file, delimiter=FileFormat.DELIMETER).writerows(Headers.EXPERIMENT_HEADERS)

            files_dict[impedance_reader] = file

        return files_dict

    def record_measurement(
        self,
        measurement_count: int,
        files: dict[ImpedanceReader, TextIOWrapper],
        reader: ImpedanceReader,
    ):
        """
        Record a measurement in the data file and on the graph. Only the first potentiostat's
        measurement is shown on the graph.

        :param measurement_count: The current measurement count.
        :param files: The process' file dictionary.
        :param reader: The **ImpedanceReader** to get data from.
        """
        csv.writer(files[reader], delimiter=FileFormat.DELIMETER).writerow(
            [
                measurement_count,
                time.time() - self.start_time(),
                reader.frequency(),
                reader.real_impedance(),
                reader.imaginary_impedance(),
                reader.impedance_standard_deviation(),
                reader.impedance_magnitude(),
                reader.impedance_phase(),
                reader.dc_current(),
                reader.dc_voltage(),
                reader.ie_range(),
            ]
        )
