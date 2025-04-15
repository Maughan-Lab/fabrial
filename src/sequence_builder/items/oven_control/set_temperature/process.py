from .....classes.process import Process, ProcessRunner
from .....classes.plotting import TemperaturePoint
from PyQt6.QtCore import pyqtSignal
from typing import Any
import time


class SetTemperatureProcess(Process):
    newDataAcquired = pyqtSignal(TemperaturePoint)

    MEASUREMENT_INTERVAL = 5
    DIRECTORY_NAME = "Set Temperature"

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)

    def run(self):
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
