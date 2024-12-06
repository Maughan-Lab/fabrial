from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QObject
from .table_model import TableModel
import time
from os import path
import os
from .constants import (
    TEMPERATURE_COLUMN,
    BUFFER_HOURS_COLUMN,
    BUFFER_MINUTES_COLUMN,
    HOLD_HOURS_COLUMN,
    HOLD_MINUTES_COLUMN,
    DATE_FORMAT,
    DATA_FILES_LOCATION,
    PRE_STABLE_FILE,
    BUFFER_FILE,
    STABLE_FILE,
    CYCLE_TIMES_FILE,
    STABILIZATON_TIMES_FILE,
    TIME,
    TEMPERATURE,
)
from instruments import InstrumentSet  # ../instruments.py
from enums.status import StabilityStatus, SequenceStatus
from typing import TextIO


class SequenceThread(QRunnable):
    """Thread for running temperature sequences."""

    # sequence specifications. There must be at least MINIMUM_MEASUREMENTS that are within
    # VARIANCE_TOLERANCE for the oven to be stable
    MINIMUM_MEASUREMENTS = 150
    VARIANCE_TOLERANCE = 1.0  # degree C
    MEASUREMENT_INTERVAL = 5.0  # seconds
    WAIT_INTERVAL = 0.01

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

            setpoint = self.model.parameter_data.item(self.cycle_number - 1, TEMPERATURE_COLUMN)
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
                BUFFER_HOURS_COLUMN, BUFFER_MINUTES_COLUMN, self.buffer_file
            )
            if not proceed:
                if not self.buffer_skip:
                    continue
                else:
                    self.buffer_skip = False

            # data collection while stable
            self.update_stability(StabilityStatus.STABLE)
            self.collect_data(HOLD_HOURS_COLUMN, HOLD_MINUTES_COLUMN, self.stable_file)

        self.post_run()

    def pre_run(self):
        """Pre-run tasks."""
        self.oven.acquire()

        self.update_status(SequenceStatus.ACTIVE)

        # this should be last
        self.starting_time = time.time()
        self.create_files(self.starting_time)

    def post_run(self):
        """Post-run tasks."""
        self.close_files()

        self.update_stability(StabilityStatus.NULL)
        self.update_status(SequenceStatus.COMPLETED if not self.cancel else SequenceStatus.CANCELED)

        self.oven.release()

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
            while len(temperature_variances) < self.MINIMUM_MEASUREMENTS:
                temperature = self.oven.read_temp()
                if temperature is not None:
                    temperature_variances.append(abs(temperature - setpoint))
                    self.record_temperature_data(self.pre_stable_file, temperature)
                else:
                    self.process_connection_problem()
                proceed = self.wait()
                if not proceed:
                    return False

            stable = True
            for location in range(len(temperature_variances)):
                variance = temperature_variances[location]
                if variance >= self.VARIANCE_TOLERANCE:
                    stable = False
                    del temperature_variances[:]
                    break

        self.record_stabilization_time()
        return True

    def collect_data(self, hours_column: str, minutes_column: str, data_file: TextIO) -> bool:
        """Collect data every **MEASUREMENT_INTERVAL** seconds."""
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
        count = 0.0
        while count < self.MEASUREMENT_INTERVAL or self.pause:
            time.sleep(self.WAIT_INTERVAL)
            count += self.WAIT_INTERVAL
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
        # create a timestamped folder to store the data files in
        os.makedirs(path.join(DATA_FILES_LOCATION, datetime), exist_ok=True)

        # open the files where this sequence will record its data
        self.pre_stable_file = open(path.join(DATA_FILES_LOCATION, datetime, PRE_STABLE_FILE), "w")
        self.buffer_file = open(path.join(DATA_FILES_LOCATION, datetime, BUFFER_FILE), "w")
        self.stable_file = open(path.join(DATA_FILES_LOCATION, datetime, STABLE_FILE), "w")
        self.cycle_times_file = open(
            path.join(DATA_FILES_LOCATION, datetime, CYCLE_TIMES_FILE), "w"
        )
        self.stabilization_times_file = open(
            path.join(DATA_FILES_LOCATION, datetime, STABILIZATON_TIMES_FILE), "w"
        )

        self.write_file_headers()  # write the file headers

    def write_file_headers(self):
        """Write the data file headers."""
        for file in (self.pre_stable_file, self.buffer_file, self.stable_file):
            file.write(self.TEMPERATURE_DATA_HEADER + "\n")
        self.cycle_times_file.write(self.CYCLE_TIMES_HEADER + "\n")
        self.stabilization_times_file.write(self.STABILIZATION_TIMES_HEADER + "\n")

    def close_files(self):
        """Close all the files."""
        for file in (
            self.pre_stable_file,
            self.buffer_file,
            self.stable_file,
            self.cycle_times_file,
            self.stabilization_times_file,
        ):
            file.close()

    def record_temperature_data(self, file: TextIO, temperature: float):
        """Write temperature data to **file**."""
        seconds_since_start, datetime = get_times(self.starting_time)
        file.write(f"{datetime},{seconds_since_start},{temperature}\n")
        self.signals.newDataAquired.emit(seconds_since_start, temperature)

    def record_cycle_time(self):
        """Record the current cycle's start time."""
        seconds_since_start, datetime = get_times(self.starting_time)
        self.cycle_times_file.write(f"{self.cycle_number},{datetime},{seconds_since_start}\n")

    def record_stabilization_time(self):
        """Record the current cycle's stabilization time."""
        seconds_since_start, datetime = get_times(self.starting_time)
        self.stabilization_times_file.write(
            f"{self.cycle_number},{datetime},{seconds_since_start}\n"
        )

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
        self.stabilty = stability
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
