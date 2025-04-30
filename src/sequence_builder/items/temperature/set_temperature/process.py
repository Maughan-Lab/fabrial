from .....classes.process import AbstractGraphingProcess
from .....classes.runners import ProcessRunner
from .....utility.temperature import create_temperature_file, record_temperature_data
from .....instruments import INSTRUMENTS, InstrumentLocker
from . import encoding
from typing import Any
import time
import os
from io import TextIOWrapper
import polars as pl


class SetTemperatureProcess(AbstractGraphingProcess):
    """
    Set the oven's temperature and record the temperature while waiting for it to stabilize.

    When subclassing, you should override:
    - `title()` - Returns the title used on the graph.
    - `metadata()` - You should probably call **Process**'s `metadata()` method.
    """

    MEASUREMENT_INTERVAL = 5000
    """Measurement interval in milliseconds."""
    MINIMUM_MEASUREMENTS = 2
    """The minimum number of measurements for stability."""
    TOLERANCE = 1.0  # degrees C
    """How far off a temperature can be from the setpoint before it is considered unstable."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)
        self.oven = INSTRUMENTS.oven
        self.temperature_file: TextIOWrapper
        self.setpoint = data[encoding.SETPOINT]

    @staticmethod
    def directory_name():
        return "Set Temperature"

    def pre_run(self):
        """Pre-run tasks. Returns whether the process should continue."""
        self.init_scatter_plot(
            self.title(),
            "Time (seconds)",
            "Temperature (°C)",
            "Oven Temperature",
        )
        self.create_files()

    def run(self):  # overridden
        with InstrumentLocker(self.oven):
            self.pre_run()
            if self.change_setpoint():
                while not self.oven.is_stable():
                    temperature = self.oven.read_temp()
                    if temperature is not None:  # we read successfully
                        self.record_temperature(temperature)
                    else:  # connection problem
                        self.error_pause()
                    if not self.wait(self.MEASUREMENT_INTERVAL, self.oven.is_connected):
                        break
            self.post_run()

    def post_run(self):
        """Post-run tasks."""
        self.temperature_file.close()
        self.write_metadata(self.metadata(time.time()))

    def create_files(self):
        """Create data files and write headers."""
        self.temperature_file = create_temperature_file(
            os.path.join(self.directory(), encoding.Filenames.TEMPERATURES)
        )

    def change_setpoint(self) -> bool:
        """
        Change the oven's setpoint, going into an error state on failure. Retry until the setpoint
        is changed. Returns whether the process should continue.
        """
        if not self.oven.change_setpoint(self.setpoint):
            self.error_pause()
            while not self.oven.change_setpoint(self.setpoint):
                if not self.wait(self.MEASUREMENT_INTERVAL, self.oven.is_connected):
                    return False
        return True

    def record_temperature(self, temperature: float):
        """Record a temperature in a file and on the graph."""
        time_since_start = record_temperature_data(
            self.temperature_file, self.start_time(), temperature
        )
        self.graphing_signals().addPoint.emit(time_since_start, temperature)

    def title(self) -> str:
        """Get the graph title."""
        return f"Set Temperature ({self.setpoint} °C)"

    def metadata(self, end_time: float) -> pl.DataFrame:  # overridden
        metadata = super().metadata(end_time)
        metadata = pl.concat(
            [pl.DataFrame({"Selected Setpoint": self.setpoint}), metadata],
            how="horizontal",
        )
        return metadata
