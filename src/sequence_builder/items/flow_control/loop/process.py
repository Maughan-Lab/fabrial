from .....classes.process import AbstractForegroundProcess
from .....classes.runners import ProcessRunner
from typing import Any


class LoopProcess(AbstractForegroundProcess):
    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        # TODO
        super().__init__(runner, data)

    def run(self):
        # TODO: implement
        print("here")
        pass

    @staticmethod
    def directory_name():
        return AbstractForegroundProcess.directory_name()
