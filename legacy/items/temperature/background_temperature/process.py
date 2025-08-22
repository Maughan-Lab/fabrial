import os
from typing import Any

from .....classes import AbstractBackgroundProcess, ProcessRunner
from .....constants.paths.process import filenames
from .....instruments import INSTRUMENTS
from .....utility import temperature as temperature_util
from . import encoding


class BackgroundTemperatureProcess(AbstractBackgroundProcess):
    """Collect and record temperature samples in the background."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        AbstractBackgroundProcess.__init__(self, runner, data, name)
        self.measurement_interval = data[encoding.MEASUREMENT_INTERVAL]

    def run(self):
        file = temperature_util.create_temperature_file(
            os.path.join(self.directory(), filenames.TEMPERATURES)
        )
        oven = INSTRUMENTS.oven
        start_time = self.start_time()

        while True:
            temperature = oven.read_temp()
            temperature_util.record_temperature_data(file, start_time, temperature)
            if not self.wait(self.measurement_interval):
                break

        file.close()

    @staticmethod
    def directory_name():
        return "Background Temperature Monitoring"
