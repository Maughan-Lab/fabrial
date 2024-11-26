from PyQt6.QtCore import QRunnable, pyqtSignal, pyqtSlot, QObject
import time
from os import path
import os
from .constants import (
    CYCLE_COLUMN,
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
from polars import col
import polars as pl
from enums.status import StabilityStatus, SequenceStatus
from typing import TextIO


class SequenceThread(QRunnable):
    """Thread for running temperature sequences."""

    # headers
    TEMPERATURE_DATA_HEADER = f"Time ({DATE_FORMAT}),{TIME},{TEMPERATURE}"
    STABILIZATION_TIMES_HEADER = (
        f"Cycle Number,Time to Stabilize ({DATE_FORMAT}),Time to Stabilize (seconds)"
    )
    CYCLE_TIMES_HEADER = f"Cycle Number,Time Cycle Began ({DATE_FORMAT}),Time Cycle Began (seconds)"

    def __init__(self, instruments: InstrumentSet, cycle_settings: pl.DataFrame):
        super().__init__()
        self.signals = Signals()

        self.oven = instruments.oven
        self.cycle_settings = cycle_settings

        self.cycle_number = 0
        self.signals.cycleNumberChanged.emit(self.cycle_number)

        self.pause = False
        self.cancel = False
        self.skip = False
        self.buffer_skip = False

    @pyqtSlot()
    def run(self):
        """Run the temperature sequence."""
        self.pre_run()

        # other stuff
        while self.cycle_number < self.cycle_settings.select(pl.len()).item():
            break
            # general process:
            #   set up the current cycle state
            #   run a stability check
            #   record data as you go
            #   buffer
            #   record data as you go
            #   record stable data
            #   repeat until there are no more setting entries
            #   end the sequence
            #   make sure you emit signals as necessary
            #   in between each data point collection, check to pause/cancel/skip/buffer skip
            #   if you get a null-read from the oven, you need to pause the sequence and
            #   try to unpause

        self.post_run(SequenceStatus.COMPLETED)

    def pre_run(self):
        # TODO: doc string
        self.oven.aquire()

        self.update_status(SequenceStatus.ACTIVE)

        # this should be last
        self.starting_time = time.time()
        self.create_files(self.starting_time)

    def post_run(self, final_status: SequenceStatus):
        # TODO: docstring
        # close all the files
        for file in (
            self.pre_stable_file,
            self.buffer_file,
            self.stable_file,
            self.cycle_times_file,
            self.stabilization_times_file,
        ):
            file.close()

        self.update_stability(StabilityStatus.NULL)
        self.update_status(final_status)

        self.oven.release()

    def check_to_proceed(self):
        """Check to pause/cancel/skip or process a connection problem."""
        pass

    def stabilize(self):
        """Collect data while waiting for the oven to stabilize."""
        # emit stability changes here
        pass

    def buffer(self):
        """Buffer and collect data."""
        pass

    def collect_data(self):
        """Collect data. The oven should be stable at this point."""
        pass

    def create_files(self, starting_time: float):
        """Initialize this sequence's data files."""
        # replace semicolons for the folder name
        datetime = convert_to_datetime(starting_time).replace(":", "ː")
        # create a timestamped folder to store the data files in
        os.mkdir(path.join(DATA_FILES_LOCATION, datetime))

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

    # TODO: implement these

    def record_temperature_data(self, file: TextIO):
        """Write temperature data to **file**."""
        pass

    def record_cycle_time(self):
        """Record the current cycle's start time."""
        pass

    def record_stabilization_time(self):
        """Record the current cycle's stabilization time."""
        pass

    # ----------------------------------------------------------------------------------------------

    def increment_cycle_number(self):
        """Increment the cycle number by 1 and emit the corresponding signal."""
        self.cycle_number += 1
        self.signals.cycleNumberChanged.emit(self.cycle_number)

    def update_status(self, status: SequenceStatus):
        self.signals.statusChanged.emit(status)

    def update_stability(self, stability: StabilityStatus):
        self.signals.stabilityChanged.emit(stability)

    # ----------------------------------------------------------------------------------------------
    def cancel_sequence(self):
        """Cancel the sequence."""
        self.cancel = True

    def pause_sequence(self):
        """Pause the sequence."""
        self.pause = True

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
    # emit these signals when a cycle/buffer is skipped
    bufferSkipped = pyqtSignal()
    cycleSkipped = pyqtSignal()


# --------------------------------------------------------------------------------------------------


def get_datetime() -> str:
    """
    Gets the current time in Day Month Year Hours:Minutes:Seconds AM/PM format. Returns "Error" if
    an error occurs.
    """
    try:
        datetime = convert_to_datetime(time.time())
    except Exception:
        datetime = "Error"
    return datetime


def convert_to_datetime(time_since_epoch: float) -> str:
    """
    Converts a float (as returned by **time.time()**) to a string in
    Day Month Year Hours:Minutes:Seconds AM/PM format.
    """
    return time.strftime("%d %B %Y %I:%M:%S %p", time.localtime(time_since_epoch))
