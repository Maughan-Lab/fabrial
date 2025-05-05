import os
from io import TextIOWrapper
from typing import Any

from ..... import Files
from .....classes.process import AbstractGraphingProcess
from .....classes.runners import ProcessRunner
from .....instruments import INSTRUMENTS, InstrumentLocker
from .....utility.dataframe import add_to_dataframe
from .....utility.temperature import create_temperature_file, record_temperature_data
from . import encoding


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

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        super().__init__(runner, data, name)
        self.oven = INSTRUMENTS.oven
        self.setpoint = data[encoding.SETPOINT]

    @staticmethod
    def directory_name():
        return "Set Temperature"

    def pre_run(self):
        """Pre-run tasks."""
        self.init_scatter_plot(
            0,
            self.title(),
            "Time (seconds)",
            "Temperature (°C)",
            "Oven Temperature",
        )

    def run(self):  # overridden
        with InstrumentLocker(self.oven):
            self.pre_run()
            if self.change_setpoint():
                with self.create_file() as file:
                    while not self.oven.is_stable():
                        temperature = self.oven.read_temp()
                        if temperature is not None:  # we read successfully
                            self.record_temperature(file, temperature)
                        else:  # connection problem
                            self.error_pause()
                        if not self.wait(self.MEASUREMENT_INTERVAL, self.oven.is_connected):
                            break

    def create_file(self) -> TextIOWrapper:
        """
        Create the data file and its write headers.

        :returns: The created file.
        """
        return create_temperature_file(
            os.path.join(self.directory(), Files.Process.Filenames.TEMPERATURES)
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

    def record_temperature(self, file: TextIOWrapper, temperature: float):
        """Record a temperature in a file and on the graph."""
        time_since_start = record_temperature_data(file, self.start_time(), temperature)
        self.graphing_signals().addPoint.emit(0, time_since_start, temperature)

    def title(self) -> str:
        """Get the graph title."""
        return f"Set Temperature ({self.setpoint} °C)"

    def metadata(self):  # overridden
        return add_to_dataframe(super().metadata(), {"Selected Setpoint": self.setpoint})
