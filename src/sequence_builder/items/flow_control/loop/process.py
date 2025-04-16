from .....classes.process import Process
from .....classes.process_runner import ProcessRunner
from typing import Any


class LoopProcess(Process):
    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        # TODO
        super().__init__(runner, data)

    def run(self):
        # TODO: implement
        pass
