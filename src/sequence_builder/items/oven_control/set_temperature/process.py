from .....classes.process import Process, ProcessRunner
from .....classes.plotting import TemperaturePoint
from ..... import Files
from .....utility.datetime import get_datetime, get_file_friendly_datatime
from . import encoding
from PyQt6.QtCore import pyqtSignal
from typing import Any
import time
import os
from io import TextIOWrapper


class SetTemperatureProcess(Process):
    newDataAcquired = pyqtSignal(float, float)  # time, temperature

    MEASUREMENT_INTERVAL = 5000  # milliseconds
    MINIMUM_MEASUREMENTS = 150
    TOLERANCE = 1.0  # degrees C

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)
        self.file_write_counter = 0
        self.temperature_file: TextIOWrapper

    def pre_run(self):
        self.create_files()

    def run(self):
        self.pre_run()
        try:
            count = 0
            end_time = time.time() + 5
            while time.time() < end_time:
                count += 1
                proceed = self.wait(10)
                if not proceed:
                    break
            # print("Started")
            # proceed = self.wait(self.MEASUREMENT_INTERVAL)
            # if not proceed:
            #     return
            # print("Just waited")
            # proceed = self.wait(self.MEASUREMENT_INTERVAL)
            # if not proceed:
            #     return
            # print("Ending")
        finally:
            self.post_run()

    def post_run(self):
        self.temperature_file.close()

    def create_files(self):
        """Create data files and write headers."""
        data_directory = os.path.join(
            self.runner().directory(),
            encoding.Filenames.DIRECTORY,
            get_file_friendly_datatime(self.start_time()),
        )
        os.makedirs(data_directory, exist_ok=True)
        self.temperature_file = open(
            os.path.join(data_directory, encoding.Filenames.TEMPERATURES), "w"
        )
        self.write_headers()

    def write_headers(self):
        """Write headers."""
        HEADERS = Files.Process.Headers.Time
        self.temperature_file.write(
            f"{HEADERS.TIME},{HEADERS.TIME_DATETIME},{encoding.Headers.OVEN_TEMPERATURE}\n"
        )
