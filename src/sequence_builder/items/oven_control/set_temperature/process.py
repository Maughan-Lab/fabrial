from .....classes.process import GraphingProcess
from .....classes.process_runner import ProcessRunner
from ..... import Files
from .....utility.datetime import get_datetime
from . import encoding
from typing import Any
import time
import os
from io import TextIOWrapper
import polars as pl


class SetTemperatureProcess(GraphingProcess):
    """
    Set the oven's temperature and record the temperature while waiting for it to stabilize.

    When subclassing this process, you must override:
    - `title()`
    - `metadata()`
    - `oven_function`
    """

    DIRECTORY = "Set Temperature"

    MEASUREMENT_INTERVAL = 5000  # milliseconds
    MINIMUM_MEASUREMENTS = 150
    TOLERANCE = 1.0  # degrees C

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)
        self.file_write_counter = 0
        self.oven = self.runner().instruments().oven
        self.temperature_file: TextIOWrapper
        self.setpoint = data[encoding.SETPOINT]

    # overridden methods
    def run(self):
        if self.pre_run():
            try:
                stable_count = 0
                while stable_count < self.MINIMUM_MEASUREMENTS:
                    temperature = self.oven.read_temp()
                    if temperature is not None:  # we read successfully
                        if abs(temperature - self.setpoint) <= self.TOLERANCE:
                            stable_count += 1
                        else:
                            stable_count = 0
                        self.record_temperature(temperature)
                    else:  # connection problem
                        self.error_pause()
                    if not self.wait(self.MEASUREMENT_INTERVAL, self.oven.is_connected):
                        break
            except Exception:
                pass
        self.post_run()

    def metadata(self, start_time: float, end_time: float):
        metadata = super().metadata(start_time, end_time)
        metadata = pl.concat(
            [pl.DataFrame({"Selected Setpoint": self.data()[encoding.SETPOINT]}), metadata],
            how="horizontal",
        )
        return metadata

    # ----------------------------------------------------------------------------------------------
    def oven_function(self) -> bool:
        """
        The function to call when changing the oven setpoint. By default, this calls
        `oven.change_setpoint()`. Returns whether the process should continue.
        """
        if not self.oven.change_setpoint(self.setpoint):
            self.error_pause()
            while not self.oven.change_setpoint(self.setpoint):
                if not self.wait(self.MEASUREMENT_INTERVAL, self.oven.is_connected):
                    return False
        return True

    def pre_run(self) -> bool:
        """Pre-run tasks. Returns whether the process should continue."""
        self.oven.acquire()
        self.init_scatter_plot(
            self.title(),
            "Time (seconds)",
            "Temperature (°C)",
            "Oven Temperature",
        )
        self.create_files()
        if not self.oven_function():
            return False
        return True

    def post_run(self):
        """Post-run tasks."""
        try:
            self.temperature_file.close()
            self.write_metadata(self.metadata(self.start_time(), time.time()))
        finally:
            self.oven.release()

    def title(self) -> str:
        """Get the graph title."""
        setpoint = self.data()[encoding.SETPOINT]
        return f"Set Temperature ({setpoint} °C)"

    def create_files(self):
        """Create data files and write headers."""
        self.temperature_file = open(
            os.path.join(self.directory(), encoding.Filenames.TEMPERATURES), "w", 1
        )
        HEADERS = Files.Process.Headers.Time
        self.temperature_file.write(
            f"{HEADERS.TIME},{HEADERS.TIME_DATETIME},{encoding.Headers.OVEN_TEMPERATURE}\n"
        )

    def record_temperature(self, temperature: float):
        """Record a temperature in a file and on the graph."""
        current_time = time.time()
        time_since_start = current_time - self.start_time()
        datetime = get_datetime(current_time)
        self.temperature_file.write(f"{time_since_start},{datetime},{temperature}\n")

        self.graph_signals.addPoint.emit(time_since_start, temperature)
