from ...base.process import BaseProcess, ProcessSignals, pyqtSignal
from .....custom_widgets.plot import PlotWidget
from .....classes.plotting import TemperaturePoint
from typing import Any


class Signals(ProcessSignals):
    newDataAcquired = pyqtSignal(TemperaturePoint)


class SetTemperatureProcess(BaseProcess):
    SIGNALS_TYPE = Signals

    MEASUREMENT_INTERVAL = 5
    DIRECTORY_NAME = "Set Temperature"

    def __init__(self, data: dict[str, Any]):
        super().__init__(data)
        self.widget = PlotWidget()

    def run(self, inputs):
        # TODO: implement
        print("We made it!")

    def visual_widget(self) -> PlotWidget:
        return self.widget
