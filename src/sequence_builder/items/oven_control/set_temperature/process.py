from .....classes.process import Process, ProcessRunner
from .....custom_widgets.plot import PlotWidget
from .....classes.plotting import TemperaturePoint
from PyQt6.QtCore import pyqtSignal
from typing import Any


class SetTemperatureProcess(Process):
    newDataAcquired = pyqtSignal(TemperaturePoint)

    WIDGET_TYPE = PlotWidget

    MEASUREMENT_INTERVAL = 5
    DIRECTORY_NAME = "Set Temperature"

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)

    def run(self):
        # widget: PlotWidget = self.widget()  # type: ignore
        print("Started")
        proceed = self.wait(self.MEASUREMENT_INTERVAL)
        if not proceed:
            return
        print("Just waited")
        proceed = self.wait(self.MEASUREMENT_INTERVAL)
        if not proceed:
            return
        print("Ending")
