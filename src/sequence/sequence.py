from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QObject
from .table_model import TableModel, Column
import time
from os import path
import os
from .constants import (
    DATE_FORMAT,
    DATA_FILES_LOCATION,
    PRE_STABLE_FILE,
    BUFFER_FILE,
    STABLE_FILE,
    CYCLE_TIMES_FILE,
    STABILIZATON_TIMES_FILE,
    GRAPH_FILE,
    TIME,
    TEMPERATURE,
)
from instruments import InstrumentSet  # ../instruments.py
from enums.status import StabilityStatus, SequenceStatus  # ../enums
from utility.graph import graph_from_folder  # ../utility
from custom_widgets.dialog import OkDialog


class SequenceThread(QRunnable):
    """Thread for running temperature sequences."""

    # sequence specifications. There must be at least MINIMUM_MEASUREMENTS that are within
    # VARIANCE_TOLERANCE for the oven to be stable
    MINIMUM_MEASUREMENTS = 150
    VARIANCE_TOLERANCE = 1.0  # degrees C
    MEASUREMENT_INTERVAL = 5.0  # seconds
    WAIT_INTERVAL = 0.01
    END_TEMPERATURE = 30  # degrees C

    # headers
    TEMPERATURE_DATA_HEADER = f"Time ({DATE_FORMAT}),{TIME},{TEMPERATURE}"
    STABILIZATION_TIMES_HEADER = (
        f"Cycle Number,Time to Stabilize ({DATE_FORMAT}),Time to Stabilize (seconds)"
    )
    CYCLE_TIMES_HEADER = f"Cycle Number,Time Cycle Began ({DATE_FORMAT}),Time Cycle Began (seconds)"

    def __init__(self, instruments: InstrumentSet, model: TableModel):
        super().__init__()
        self.signals = Signals()

        self.oven = instruments.oven
        self.model = model

        self.cycle_number = 0

        self.pause = False
        self.cancel = False
        self.skip = False
        self.buffer_skip = False
        self.connection_problem = False
        self.stability = StabilityStatus.NULL
        self.old_stability = StabilityStatus.NULL

    @pyqtSlot()
    def run(self):
        """Run the temperature sequence."""
        self.pre_run()

        # other stuff
        while self.cycle_number < self.model.rowCount() and not self.cancel:
            self.increment_cycle_number()
            self.record_cycle_time()

            # self.change_setpoint() will wait until the operation is successful
            setpoint = self.model.parameter_data.item(
                self.cycle_number - 1, str(Column.TEMPERATURE)
            )
            proceed = self.change_setpoint(setpoint)
            if not proceed:
                continue

            # stabilizing
            self.update_stability(StabilityStatus.CHECKING)
            proceed = self.stabilize(setpoint)
            if not proceed:
                continue

            # buffering
            self.update_stability(StabilityStatus.BUFFERING)
            proceed = self.collect_data(
                str(Column.BUFFER_HOURS), str(Column.BUFFER_MINUTES), self.buffer_file
            )
            if not proceed:
                if not self.buffer_skip:
                    continue
                else:
                    self.buffer_skip = False

            # data collection while stable
            self.update_stability(StabilityStatus.STABLE)
            self.collect_data(str(Column.HOLD_HOURS), str(Column.HOLD_MINUTES), self.stable_file)

        self.post_run()

    def pre_run(self):
        """Pre-run tasks."""
        self.update_status(SequenceStatus.ACTIVE)
        self.oven.acquire()

        # this should be last
        self.starting_time = time.time()
        self.create_files(self.starting_time)

    def post_run(self):
        """Post-run tasks."""
        if self.cancel:
            final_status = SequenceStatus.CANCELED
        else:
            # if the sequence finishes naturally, set the oven to the END_TEMPERATURE
            self.change_setpoint(self.END_TEMPERATURE)
            final_status = SequenceStatus.COMPLETED
        self.graph_and_save()

        self.oven.release()
        self.update_stability(StabilityStatus.NULL)
        self.update_status(final_status)

    def change_setpoint(self, setpoint: float) -> bool:
        """
        Change the setpoint (blocks until the setpoint is set or the sequence is interrupted).
        Returns whether the sequence should proceed.
        """
        proceed = True
        while not self.oven.change_setpoint(setpoint):
            self.process_connection_problem()
            proceed = self.wait()
            if not proceed:
                break
        return proceed

    def stabilize(self, setpoint: float) -> bool:
        """Collect data while waiting for the oven to stabilize."""
        temperature_variances: list[float] = []
        stable = False
        while not stable:
            while True:
                temperature = self.oven.read_temp()
                if temperature is not None:
                    temperature_variances.append(abs(temperature - setpoint))
                    self.record_temperature_data(self.pre_stable_file, temperature)
                else:
                    self.process_connection_problem()

                # check to proceed
                proceed = self.wait()
                if not proceed:
                    return False

                if len(temperature_variances) >= self.MINIMUM_MEASUREMENTS:
                    break  # we're good to check the stability

            stable = True
            # start from the end of the list and search for the first instance of an "unstable"
            # measurement. If one is not found, we're stable!
            # we must start from the end because we want to eliminate as much of the list as
            # possible
            length = len(temperature_variances)
            for index in range(length - 1, -1, -1):
                variance = temperature_variances[index]
                if variance >= self.VARIANCE_TOLERANCE:
                    stable = False
                    # we delete the list from the "unstable" point and before, and keep the rest
                    # the garbage collector will remove the rest of the list
                    if (index + 1) == length:
                        # if the "unstable" point was the last point in the list, remove the whole
                        # list
                        temperature_variances = []
                    else:
                        # otherwise remove the "unstable" point and everything before
                        temperature_variances = temperature_variances[index + 1 :]
                    break

        self.record_stabilization_time()
        return True

    def collect_data(self, hours_column: str, minutes_column: str, data_file: str) -> bool:
        """Collect data every **MEASUREMENT_INTERVAL** seconds and write data to **data_file**."""
        hours: int = self.model.parameter_data.item(self.cycle_number - 1, hours_column)
        minutes: int = self.model.parameter_data.item(self.cycle_number - 1, minutes_column)
        repeat_count = (hours * 3600 + minutes * 60) / self.MEASUREMENT_INTERVAL
        current_count = 0
        while current_count < repeat_count:
            temperature = self.oven.read_temp()
            if temperature is not None:
                self.record_temperature_data(data_file, temperature)
            else:
                self.process_connection_problem()
            proceed = self.wait()
            if not proceed:
                return False
            current_count += 1
        return True

    def wait(self) -> bool:
        """
        Wait for **MEASUREMENT_INTERVAL** or while there is a connection problem. Returns
        True if the cycle should proceed, False otherwise (i.e. the cycle is canceled or skipped).
        """
        end_time = time.time() + self.MEASUREMENT_INTERVAL
        while time.time() < end_time or self.pause:
            time.sleep(self.WAIT_INTERVAL)
            if self.cancel:
                return False
            elif self.skip:
                self.skip = False
                return False
            elif self.buffer_skip:
                return False
            if self.connection_problem:
                if self.oven.is_connected():
                    self.connection_problem = False
                    self.unpause_sequence()
                    self.update_stability(self.old_stability)
        return True

    def process_connection_problem(self):
        self.connection_problem = True
        self.pause_sequence()
        self.old_stability = self.stability
        self.update_stability(StabilityStatus.ERROR)

    # ----------------------------------------------------------------------------------------------
    # file IO
    def create_files(self, starting_time: float):
        """Initialize this sequence's data files."""
        # replace semicolons for the folder name
        datetime = convert_to_datetime(starting_time).replace(":", "ː")
        self.data_folder = path.join(DATA_FILES_LOCATION, datetime)
        # create a timestamped folder to store the data files in
        os.makedirs(self.data_folder, exist_ok=True)

        # get the names of the files where this sequence will record its data
        self.pre_stable_file = path.join(self.data_folder, PRE_STABLE_FILE)
        self.buffer_file = path.join(self.data_folder, BUFFER_FILE)
        self.stable_file = path.join(self.data_folder, STABLE_FILE)
        self.cycle_times_file = path.join(self.data_folder, CYCLE_TIMES_FILE)
        self.stabilization_times_file = path.join(self.data_folder, STABILIZATON_TIMES_FILE)

        self.write_file_headers()  # write the file headers

    def write_file_headers(self):
        """Write the data file headers."""
        for file in (self.pre_stable_file, self.buffer_file, self.stable_file):
            self.write_csv_line(file, self.TEMPERATURE_DATA_HEADER, file_mode="w")
        self.write_csv_line(self.cycle_times_file, self.CYCLE_TIMES_HEADER, file_mode="w")
        self.write_csv_line(
            self.stabilization_times_file, self.STABILIZATION_TIMES_HEADER, file_mode="w"
        )

    def record_temperature_data(self, file: str, temperature: float):
        """Write temperature data to **file**."""
        seconds_since_start, datetime = get_times(self.starting_time)
        self.write_csv_line(file, datetime, seconds_since_start, temperature)
        self.signals.newDataAquired.emit(seconds_since_start, temperature)

    def record_cycle_time(self):
        """Record the current cycle's start time."""
        seconds_since_start, datetime = get_times(self.starting_time)
        self.write_csv_line(self.cycle_times_file, self.cycle_number, datetime, seconds_since_start)

    def record_stabilization_time(self):
        """Record the current cycle's stabilization time."""
        seconds_since_start, datetime = get_times(self.starting_time)
        self.write_csv_line(
            self.stabilization_times_file, self.cycle_number, datetime, seconds_since_start
        )

    def write_csv_line(self, file: str, *values: float | str, file_mode: str = "a"):
        """
        Write a line in a csv file. The line will end with a newline character.

        :param file: The file to write to.
        :param *values: The values to write to the file. Each value will be comma separated.
        :param file_mode: The mode to open the file in. Must grant write privileges.
        Defaults to "a" (append) mode.
        """
        if len(values) == 1:
            line = f"{values[0]}\n"
        else:
            line = ""
            for value in values[:-1]:
                line += f"{value},"
            line += f"{values[-1]}\n"
        with open(file, file_mode) as f:
            f.write(line)

    def graph_and_save(self):
        """Graph the sequence on one plot and save the figure."""
        try:
            graph_from_folder(self.data_folder).savefig(
                path.join(self.data_folder, GRAPH_FILE), dpi=1000
            )
        except Exception:
            OkDialog(
                "Graphing Failed",
                "Unable to graph sequence data upon finishing the sequence. Data is saved.",
            ).exec()

    # ----------------------------------------------------------------------------------------------
    # signals
    def increment_cycle_number(self):
        """Increment the cycle number by 1 and emit the corresponding signal."""
        self.cycle_number += 1
        self.signals.cycleNumberChanged.emit(self.cycle_number)

    def update_status(self, status: SequenceStatus):
        """Emit the supplied SequenceStatus."""
        self.signals.statusChanged.emit(status)

    def update_stability(self, stability: StabilityStatus):
        """Emit the supplied StabilityStatus."""
        self.stability = stability
        self.signals.stabilityChanged.emit(stability)

    # ----------------------------------------------------------------------------------------------
    # external command handlers
    def cancel_sequence(self):
        """Cancel the sequence."""
        self.cancel = True

    def pause_sequence(self):
        """Pause the sequence."""
        self.pause = True
        self.update_status(SequenceStatus.PAUSED)

    def unpause_sequence(self):
        """Unpause the sequence."""
        self.pause = False
        self.update_status(SequenceStatus.ACTIVE)

    def skip_cycle(self):
        """Skip the current cycle."""
        self.skip = True

    def skip_buffer(self):
        """Skip just the current buffer."""
        self.buffer_skip = True


class Signals(QObject):
    """Signals for the SequenceThread."""

    newDataAquired = pyqtSignal(float, float)
    cycleNumberChanged = pyqtSignal(int)
    stabilityChanged = pyqtSignal(StabilityStatus)
    statusChanged = pyqtSignal(SequenceStatus)


# --------------------------------------------------------------------------------------------------
def convert_to_datetime(time_since_epoch: float) -> str:
    """
    Converts a float (as returned by **time.time()**) to a string in
    Day Month Year Hours:Minutes:Seconds AM/PM format.
    """
    return time.strftime("%d %B %Y %I:%M:%S %p", time.localtime(time_since_epoch))


def get_times(starting_time: float) -> tuple[float, str]:
    current_time = time.time()
    return (current_time - starting_time, convert_to_datetime(current_time))
