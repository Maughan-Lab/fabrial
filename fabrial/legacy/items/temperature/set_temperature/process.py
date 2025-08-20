import os
from io import TextIOWrapper
from typing import Any

from .....classes import AbstractGraphingProcess, ProcessRunner
from .....constants.paths.process import filenames
from .....instruments import INSTRUMENTS, InstrumentLocker
from .....utility import dataframe, temperature as temperature_util
from . import encoding


class SetTemperatureProcess(AbstractGraphingProcess):
    """
    Set the oven's temperature and record the temperature while waiting for it to stabilize.

    When subclassing, you should override:
    - `title()` - Returns the title used on the graph.
    - `metadata()` - You should probably call `Process`'s `metadata()` method.
    """

    MEASUREMENT_INTERVAL = 5000
    """Measurement interval in milliseconds."""
    MINIMUM_MEASUREMENTS = 2
    """The minimum number of measurements for stability."""
    TOLERANCE = 1.0  # degrees C
    """How far off a temperature can be from the setpoint before it is considered unstable."""
    GRAPH_FILENAME = "graph.png"
    """The name used for the graph."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        AbstractGraphingProcess.__init__(self, runner, data, name)
        self.oven = INSTRUMENTS.oven
        self.setpoint = data[encoding.SETPOINT]

        self.file: TextIOWrapper

    @staticmethod
    def directory_name():
        return "Set Temperature"

    def pre_run(self):
        """Pre-run tasks."""
        self.init_scatter_plot(
            0,
            "Temperature Graph",
            self.title(),
            "Time (seconds)",
            "Temperature (°C)",
            "Oven Temperature",
        )
        self.create_file()

    def run(self):
        try:
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
        finally:
            self.post_run()

    def post_run(self):
        """Post-run tasks."""
        self.file.close()
        self.graphing_signals().saveFig.emit(0, os.path.join(self.directory(), self.GRAPH_FILENAME))

    def create_file(self):
        """
        Create the data file and its write headers.

        Returns
        -------
        The created file.
        """
        self.file = temperature_util.create_temperature_file(
            os.path.join(self.directory(), filenames.TEMPERATURES)
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
        time_since_start = temperature_util.record_temperature_data(
            self.file, self.start_time(), temperature
        )
        self.graphing_signals().addPoint.emit(0, time_since_start, temperature)

    def title(self) -> str:
        """Get the graph title."""
        return f"Set Temperature ({self.setpoint} °C)"

    def metadata(self):  # overridden
        return dataframe.add_to_dataframe(
            AbstractGraphingProcess.metadata(self), {"Selected Setpoint": self.setpoint}
        )
