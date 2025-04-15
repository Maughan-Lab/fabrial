from .....classes.process import Process, ProcessRunner
from typing import Any


class LoopProcess(Process):
    def __init__(self, runner: ProcessRunner, data: dict[str, Any] | None = None):
        # TODO
        super().__init__(runner, data)

    def run(self):
        # TODO: implement
        pass
