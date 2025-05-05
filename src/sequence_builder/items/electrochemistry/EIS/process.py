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
from .....gamry_integration.gamry import GAMRY, ImpedanceReader, Potentiostat
from .....utility.dataframe import add_to_dataframe
from . import encoding
from .encoding import FileFormat, Headers


class EISProcess(AbstractGraphingProcess):
    """Run a clone of the Gamry Potentiostatic EIS.exp file."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        super().__init__(runner, data, name)
        # unpack the dictionary values for easier access
        self.initial_frequency: float = data[encoding.INITIAL_FREQUENCY]
        self.final_frequency: float = data[encoding.FINAL_FREQUENCY]
        self.points_per_decade: int = data[encoding.POINTS_PER_DECADE]
        self.ac_voltage: float = data[encoding.AC_VOLTAGE] / 1000  # convert from mV to V
        self.dc_voltage: float = data[encoding.DC_VOLTAGE]
        self.area: float = data[encoding.AREA]
        self.impedance_guess: float = data[encoding.ESTIMATED_IMPEDANCE]
        self.pstat_identifiers: list[str] = data[encoding.SELECTED_PSTATS]

        self.files: dict[ImpedanceReader, TextIOWrapper]
        self.plot_indexes: dict[ImpedanceReader, int]

    def pre_run(self, impedance_readers: Iterable[ImpedanceReader], context_manager: ExitStack):
        """Pre-run tasks."""
        self.create_files(impedance_readers, context_manager)
        self.init_plots(impedance_readers)

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

        # open all files, potentiostats, and impedance readers using a context manager so they get
        # closed automatically
        with ExitStack() as context_manager:
            impedance_readers = self.create_impedance_readers(context_manager)
            # do the first measurement (I think to get the potentiostats ready)
            for impedance_reader in impedance_readers:
                impedance_reader.measure(self.initial_frequency, self.ac_voltage)

            self.pre_run(impedance_readers, context_manager)

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
                                {QMessageBox.StandardButton.Yes: "Next"},
                            )
                            match self.wait_on_response():
                                case QMessageBox.StandardButton.Yes:  # next measurement
                                    break
                                case QMessageBox.StandardButton.Retry:  # retry measurement
                                    continue
                                case QMessageBox.StandardButton.Abort:  # abort experiment
                                    self.cancel()
                                    break

                    if self.is_canceled():
                        break
                    self.record_measurement(measurement_count, impedance_reader)

                measurement_count += 1
                if not self.wait(50):
                    break

            self.post_run(impedance_readers)

    def post_run(self, impedance_readers: Iterable[ImpedanceReader]):
        """Post-run tasks."""
        # save the bode plots for each potentiostat
        for impedance_reader in impedance_readers:
            identifier = impedance_reader.potentiostat().identifier()
            self.graphing_signals().saveFig.emit(
                self.plot_indexes[impedance_reader], f"{identifier}.png"
            )

    @staticmethod
    def directory_name():
        return "Electrochemical Impedance Spectroscopy"

    def create_impedance_readers(self, context_manager: ExitStack) -> list[ImpedanceReader]:
        """
        Create, initialize, and return the process' impedance readers.

        :param context_manager: The context manager used to automatically close and cleanup the
        devices.
        """
        impedance_readers: list[ImpedanceReader] = []
        # create, open, and initialize the pstats and impedance readers
        for identifer in self.pstat_identifiers:
            potentiostat = context_manager.enter_context(
                Potentiostat(GAMRY.com_interface(), identifer)
            ).initialize(self.dc_voltage, self.impedance_guess)

            impedance_reader = context_manager.enter_context(
                ImpedanceReader(potentiostat)
            ).initialize(self.impedance_guess)
            impedance_readers.append(impedance_reader)

        return impedance_readers

    def create_files(self, readers: Iterable[ImpedanceReader], context_manager: ExitStack):
        """
        Create the data files and their write headers.

        :param readers: The impedance readers being used by the process.
        :param context_manager: The context manager used to automatically close the files.
        """
        self.files = dict()
        for impedance_reader in readers:
            identifier = impedance_reader.potentiostat().identifier()
            # file names are based on the potentiostat identifier
            file = context_manager.enter_context(
                open(
                    os.path.join(self.directory(), f"{identifier}.DTA"),
                    "w",
                    1,
                    newline="",
                )
            )
            writer = csv.writer(file, delimiter=FileFormat.DELIMETER)
            writer.writerows(Headers.EXPERIMENT_HEADERS)
            # from what I saw in the Potentiostatic EIS.exp file, the only use of the area is to
            # record it
            writer.writerow(["AREA", "QUANT", str(self.area), "&Area (cm^2)"])

            self.files[impedance_reader] = file

    def init_plots(self, readers: Iterable[ImpedanceReader]):
        """Initialize the plots."""
        self.plot_indexes = dict()
        for index, impedance_reader in enumerate(readers):
            identifier = impedance_reader.potentiostat().identifier()
            self.init_scatter_plot(
                index,
                identifier,
                f"Bode Plot for {identifier}",
                "Frequency (Hz)",
                "Impedance Magnitude (kΩ)",
                "Z-Curve",
                symbol_color="lightskyblue",
            )
            self.graphing_signals().setLogScale.emit(index, True, False)
            self.plot_indexes[impedance_reader] = index

    def record_measurement(self, measurement_count: int, reader: ImpedanceReader):
        """
        Record a measurement in the data file and on the graph. Only the first potentiostat's
        measurement is shown on the graph.

        :param measurement_count: The current measurement count.
        :param reader: The **ImpedanceReader** to get data from.
        """
        frequency = reader.frequency()
        impedance_magnitude = reader.impedance_magnitude()
        csv.writer(self.files[reader], delimiter=FileFormat.DELIMETER).writerow(
            [
                "",  # for initial tab
                measurement_count,
                time.time() - self.start_time(),
                frequency,
                reader.real_impedance(),
                reader.imaginary_impedance(),
                reader.impedance_standard_deviation(),
                impedance_magnitude,
                reader.impedance_phase(),
                reader.dc_current(),
                reader.dc_voltage(),
                reader.ie_range(),
            ]
        )
        self.graphing_signals().addPoint.emit(
            self.plot_indexes[reader], frequency, impedance_magnitude / 1000  # convert to kΩ
        )

    def metadata(self):  # overridden
        return add_to_dataframe(
            super().metadata(),
            {
                encoding.SELECTED_PSTATS: " ".join(self.pstat_identifiers),  # space separate them
                encoding.DC_VOLTAGE: self.dc_voltage,
                encoding.INITIAL_FREQUENCY: self.initial_frequency,
                encoding.FINAL_FREQUENCY: self.final_frequency,
                encoding.POINTS_PER_DECADE: self.points_per_decade,
                encoding.AC_VOLTAGE: self.ac_voltage,
                encoding.AREA: self.area,
                encoding.ESTIMATED_IMPEDANCE: self.impedance_guess,
            },
        )
