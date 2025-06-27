from typing import Any

from polars import DataFrame

from .....classes.process import AbstractForegroundProcess
from .....classes.runners import ProcessRunner
from .....instruments import INSTRUMENTS
from .....utility.dataframe import add_to_dataframe
from . import encoding


class SetNoStabilizeProcess(AbstractForegroundProcess):
    """Set the oven's setpoint without waiting to stabilize."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        super().__init__(runner, data, name)
        self.oven = INSTRUMENTS.oven
        self.setpoint = data[encoding.SETPOINT]

    @staticmethod
    def directory_name() -> str:
        return "Set Temperature (No Stabilization)"

    def run(self):
        # change the oven's setpoint and make sure it actually happens
        while not self.oven.change_setpoint(self.setpoint):
            if not self.wait(50, self.oven.is_connected):
                break

    def metadata(self) -> DataFrame:
        return add_to_dataframe(super().metadata(), {"Selected Setpoint": self.setpoint})
