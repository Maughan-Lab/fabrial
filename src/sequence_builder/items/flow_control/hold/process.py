from typing import Any

from .....classes.process import AbstractForegroundProcess
from .....classes.runners import ProcessRunner
from . import encoding


class HoldProcess(AbstractForegroundProcess):
    """Hold for a duration."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)
        hours: int = data[encoding.HOURS]
        minutes: int = data[encoding.MINUTES]
        seconds: int = data[encoding.SECONDS]
        self.duration = (hours * 3600 + minutes * 60 + seconds) * 1000  # in milliseconds

    def run(self):
        self.errorOccurred.emit("fuck")
        self.wait(self.duration)  # I didn't think it would be that simple lmao

    @staticmethod
    def directory_name():
        return "Hold"
