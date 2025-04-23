from .....classes.process import GraphingProcess
from .....classes.process_runner import ProcessRunner
from ..... import Files
from . import encoding
from typing import Any
import time
import os
from io import TextIOWrapper


class SetTemperatureProcess(GraphingProcess):
    DIRECTORY = "Set Temperature"

    MEASUREMENT_INTERVAL = 5000  # milliseconds
    MINIMUM_MEASUREMENTS = 150
    TOLERANCE = 1.0  # degrees C

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)
        self.file_write_counter = 0
        self.oven = self.runner().instruments().oven
        self.temperature_file: TextIOWrapper

    def pre_run(self):
        self.init_scatter_plot(
            "Oven Temperature", "Time (seconds)", "Temperature (°C)", "Oven Temperature"
        )
        self.create_files()

    def run(self):
        self.pre_run()

        try:
            self.oven.acquire()

            # TODO: actually implement
            count = 0
            end_time = time.time() + 5
            while time.time() < end_time:
                count += 1
                proceed = self.wait(10)
                if not proceed:
                    break
        finally:
            self.post_run()

    def post_run(self):
        try:
            self.temperature_file.close()
            self.write_metadata(self.directory(), self.start_time(), time.time())
        finally:
            self.oven.release()

    def create_files(self):
        """Create data files and write headers."""
        self.temperature_file = open(
            os.path.join(self.directory(), encoding.Filenames.TEMPERATURES), "w"
        )
        HEADERS = Files.Process.Headers.Time
        self.temperature_file.write(
            f"{HEADERS.TIME},{HEADERS.TIME_DATETIME},{encoding.Headers.OVEN_TEMPERATURE}\n"
        )
