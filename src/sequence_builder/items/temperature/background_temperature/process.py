import os
from typing import Any

from ..... import Files
from .....classes.process import AbstractBackgroundProcess
from .....classes.runners import ProcessRunner
from .....instruments import INSTRUMENTS
from .....utility.temperature import create_temperature_file, record_temperature_data
from . import encoding


class BackgroundTemperatureProcess(AbstractBackgroundProcess):
    """Collect and record temperature samples in the background."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        super().__init__(runner, data, name)
        self.measurement_interval = data[encoding.MEASUREMENT_INTERVAL]

    def run(self):
        file = create_temperature_file(
            os.path.join(self.directory(), Files.Process.Filenames.TEMPERATURES)
        )
        oven = INSTRUMENTS.oven
        start_time = self.start_time()

        while True:
            temperature = oven.read_temp()
            record_temperature_data(file, start_time, temperature)
            if not self.wait(self.measurement_interval):
                break

        file.close()

    @staticmethod
    def directory_name():
        return "Background Temperature Monitoring"
