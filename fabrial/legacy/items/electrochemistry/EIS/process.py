import csv
import math
import os
import time
from collections.abc import Iterable
from contextlib import ExitStack
from dataclasses import dataclass
from io import TextIOWrapper
from typing import Any

from PyQt6.QtWidgets import QMessageBox

from .....classes import AbstractGraphingProcess, ProcessRunner
from .....gamry_integration import GAMRY, ImpedanceReader, Potentiostat
from .....utility import dataframe
from . import encoding
from .encoding import FileFormat, Headers

try:
    from comtypes import client  # type: ignore
except ImportError:
    pass


@dataclass
class ImpedanceReaderData:
    file: TextIOWrapper
    plot_index: int
    frequency: float
    measurement_count: int = 0
    calibration_measurement: bool = True
    retry_count: int = 0


class EISProcess(AbstractGraphingProcess):
    """Run a clone of the Gamry Potentiostatic EIS.exp file."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        AbstractGraphingProcess.__init__(self, runner, data, name)
        # unpack the dictionary values for easier access
        self.initial_frequency: float = data[encoding.INITIAL_FREQUENCY]
        self.final_frequency: float = data[encoding.FINAL_FREQUENCY]
        self.points_per_decade: int = data[encoding.POINTS_PER_DECADE]
        self.ac_voltage: float = data[encoding.AC_VOLTAGE] / 1000  # convert from mV to V
        self.dc_voltage: float = data[encoding.DC_VOLTAGE]
        self.vs_open_circuit_voltage = data[encoding.DC_VOLTAGE_REFERENCE] == encoding.VS_EOC
        self.impedance_guess: float = data[encoding.ESTIMATED_IMPEDANCE]
        self.impedance_reader_speed_option: str = data[encoding.IMPEDANCE_READER_SPEED]
        self.pstat_identifiers: list[str] = data[encoding.SELECTED_PSTATS]

        self.log_increment = 1 / self.points_per_decade
        if self.initial_frequency > self.final_frequency:
            # if we are sweeping high frequency to low frequency, we need to decrease in frequency
            self.log_increment = -self.log_increment

        self.maximum_measurements = math.ceil(
            abs(math.log10(self.final_frequency) - math.log10(self.initial_frequency))
            * self.points_per_decade
        )

        self.impedance_reader_data: dict[ImpedanceReader, ImpedanceReaderData] = dict()

    def run(self) -> None:
        # open all files, potentiostats, and impedance readers using a context manager so they
        # get closed automatically
        with ExitStack() as context_manager:
            impedance_readers = self.create_impedance_readers(context_manager)
            try:
                # do the first measurement (this starts a chain)
                for impedance_reader in impedance_readers:
                    impedance_reader.measure(self.initial_frequency, self.ac_voltage)
                # run while at least one impedance reader still has measurements to do or until we
                # get #canceled
                while not self.is_canceled():
                    # this causes a bunch of signals to fire which do most of the data acquisition
                    # and recording
                    client.PumpEvents(0.1)
                    self.wait(50)
                    for impedance_reader in impedance_readers:
                        if not self.is_finished(impedance_reader):
                            break
                    else:  # the for loop finished naturally
                        break
            except Exception:
                pass
            finally:
                self.post_run(impedance_readers)

    def post_run(self, impedance_readers: Iterable[ImpedanceReader]):
        """Post-run tasks."""
        # save the bode plots for each potentiostat
        for impedance_reader in impedance_readers:
            impedance_reader_data = self.impedance_reader_data[impedance_reader]
            identifier = impedance_reader.potentiostat().identifier()
            self.graphing_signals().saveFig.emit(
                impedance_reader_data.plot_index,
                os.path.join(self.directory(), f"{identifier}.png"),
            )

    @staticmethod
    def directory_name():
        return "Electrochemical Impedance Spectroscopy"

    def handle_data_ready(self, impedance_reader: ImpedanceReader, success: bool):
        """
        Handle data being ready for an impedance reader. The first measurement is run twice; the
        first time calibrates the potentiostat and the second time actually records data.
        """
        # unless the impedance reader is finished with its frequency sweep, each call to this
        # function will queue another call for the same impedance reader
        if self.is_canceled():
            return

        impedance_reader_data = self.impedance_reader_data[impedance_reader]

        if impedance_reader_data.calibration_measurement:  # if this is the calibration measurement
            impedance_reader_data.calibration_measurement = False
            impedance_reader.measure(impedance_reader_data.frequency, self.ac_voltage)
            return

        if not success:
            # if we failed to read, retry 10 times
            if impedance_reader_data.retry_count < 10:
                impedance_reader.measure(impedance_reader_data.frequency, self.ac_voltage)
                impedance_reader_data.retry_count += 1
                return
            # if we still failed, ask the user what to do
            identifer = impedance_reader.potentiostat().identifier()
            self.send_message(
                f"Failed to take measurement for potentiostat {identifer} "
                f"at frequency {impedance_reader_data.frequency}. "
                "Continue to next frequency, retry measurement, "
                "or abort experiment?",
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.Retry
                | QMessageBox.StandardButton.Abort,
                {QMessageBox.StandardButton.Yes: "Next"},
            )
            response = self.wait_on_response()
            if response is None:  # the process has been canceled
                return
            match response:
                case QMessageBox.StandardButton.Yes:  # next measurement
                    pass
                case QMessageBox.StandardButton.Retry:  # retry measurement
                    impedance_reader_data.retry_count = 0
                    impedance_reader.measure(impedance_reader_data.frequency, self.ac_voltage)
                    return
                case QMessageBox.StandardButton.Abort:  # abort experiment
                    self.cancel()
                    return

        # if we are here the measurement either succeeded or was skipped (so move to next frequency)
        self.record_measurement(impedance_reader_data.measurement_count, impedance_reader)

        impedance_reader_data.measurement_count += 1
        if not self.is_finished(impedance_reader):
            desired_frequency = math.pow(
                10,
                math.log10(self.initial_frequency)
                + impedance_reader_data.measurement_count * self.log_increment,
            )
            impedance_reader_data.frequency = desired_frequency
            impedance_reader.measure(impedance_reader_data.frequency, self.ac_voltage)

    def is_finished(self, impedance_reader: ImpedanceReader) -> bool:
        """Whether the impedance reader has finished its frequency sweep."""
        measurement_count = self.impedance_reader_data[impedance_reader].measurement_count
        if measurement_count > self.maximum_measurements:
            return True
        return False

    def create_impedance_readers(self, context_manager: ExitStack) -> list[ImpedanceReader]:
        """
        Create, initialize, and return the process' impedance readers.

        Parameters
        ----------
        context_manager
            The context manager used to automatically close and cleanup the devices.
        """
        impedance_readers: list[ImpedanceReader] = []
        for index, identifer in enumerate(self.pstat_identifiers):
            # make the potentiostat
            potentiostat = context_manager.enter_context(
                Potentiostat(GAMRY.com_interface(), identifer)
            )
            # measure the open circuit voltage to calculate the voltage vs. Eref
            if self.vs_open_circuit_voltage:
                open_circuit_voltage = potentiostat.measure_open_circuit_voltage()
                voltage_vs_reference = self.dc_voltage + open_circuit_voltage
            else:
                voltage_vs_reference = self.dc_voltage
            potentiostat.initialize(voltage_vs_reference)
            # make the impedance reader
            impedance_reader = context_manager.enter_context(
                ImpedanceReader(potentiostat)
            ).initialize(
                self.impedance_guess,
                encoding.IMPEDANCE_READER_SPEED_DICT[self.impedance_reader_speed_option],
            )
            impedance_readers.append(impedance_reader)
            # connect the impedance reader's signals
            # this is weirdly written because non-primitive types are passed by pointer for signals
            impedance_reader.dataReady.connect(
                lambda success, reader=impedance_reader: self.handle_data_ready(reader, success)
            )
            # make the file for the reader
            file = self.create_file(impedance_reader, context_manager)
            # initialize the plot for the reader
            self.init_plot(impedance_reader, index)
            # create a new entry in the impedance reader bookkeeping dictionary
            self.impedance_reader_data[impedance_reader] = ImpedanceReaderData(
                file, index, self.initial_frequency
            )

        return impedance_readers

    def create_file(
        self, impedance_reader: ImpedanceReader, context_manager: ExitStack
    ) -> TextIOWrapper:
        """
        Create the data file for an impedance reader and their write the header.

        Parameters
        ----------
        reader
            The impedance reader to create the file for.
        context_manager
            The context manager used to automatically close the file.
        """
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
        writer.writerows(Headers.GAMRY_HEADERS)
        writer.writerows(Headers.DATA_HEADERS)

        return file

    def init_plot(self, impedance_reader: ImpedanceReader, index: int):
        """Initialize the plot for an impedance reader."""
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

    def record_measurement(self, measurement_count: int, reader: ImpedanceReader):
        """
        Record a measurement in the data file and on the graph. Only the first potentiostat's
        measurement is shown on the graph.

        Parameters
        ----------
        measurement_count
            The current measurement count.
        reader
            The `ImpedanceReader` to get data from.
        """
        impedance_reader_data = self.impedance_reader_data[reader]

        frequency = reader.frequency()
        impedance_magnitude = reader.impedance_magnitude()
        csv.writer(impedance_reader_data.file, delimiter=FileFormat.DELIMETER).writerow(
            [
                "",  # for initial tab
                measurement_count,
            ]
            + [
                round(value, 6)
                for value in [
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
            ]
        )
        self.graphing_signals().addPoint.emit(
            impedance_reader_data.plot_index, frequency, impedance_magnitude / 1000  # convert to kΩ
        )

    def metadata(self):  # overridden
        return dataframe.add_to_dataframe(
            AbstractGraphingProcess.metadata(self),
            {
                encoding.SELECTED_PSTATS: " ".join(self.pstat_identifiers),  # space separate them
                encoding.DC_VOLTAGE: self.dc_voltage,
                encoding.DC_VOLTAGE_REFERENCE: self.data()[encoding.DC_VOLTAGE_REFERENCE],
                encoding.INITIAL_FREQUENCY: self.initial_frequency,
                encoding.FINAL_FREQUENCY: self.final_frequency,
                encoding.POINTS_PER_DECADE: self.points_per_decade,
                encoding.AC_VOLTAGE: self.data()[encoding.AC_VOLTAGE],  # mV
                encoding.ESTIMATED_IMPEDANCE: self.impedance_guess,
                encoding.IMPEDANCE_READER_SPEED: self.impedance_reader_speed_option,
            },
        )
