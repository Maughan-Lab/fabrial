from .....classes.process import Process, ProcessRunner
from .....custom_widgets.plot import PlotWidget
from .....classes.plotting import TemperaturePoint
from .....enums.status import SequenceStatus
from PyQt6.QtCore import pyqtSignal
from typing import Any
import time


class SetTemperatureProcess(Process):
    newDataAcquired = pyqtSignal(TemperaturePoint)

    WIDGET_TYPE = PlotWidget

    MEASUREMENT_INTERVAL = 5
    DIRECTORY_NAME = "Set Temperature"

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)

    def run(self):
        end_time = time.time() + 3
        while time.time() < end_time:
            if self.is_paused():
                print("pause detected")
                pass
            time.sleep(0.1)
