from .....classes.process import AbstractForegroundProcess
from .....classes.runners import ProcessRunner
from . import encoding
from typing import Any


class LoopProcess(AbstractForegroundProcess):
    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):
        super().__init__(runner, data)
        self.number_of_loops = data[encoding.NUMBER_OF_LOOPS]

    def run(self) -> None:
        # reconfigure the runner while saving previous values
        runner = self.runner()
        previous_directory = runner.directory()
        previous_number = runner.number()
        runner.set_directory(self.directory())
        runner.reset_number()

        # run each item
        loop_item = runner.current_item()
        if loop_item is not None:
            for _ in range(self.number_of_loops):
                for item in loop_item.subitems():
                    process_type = item.process_type()
                    if process_type is not None:
                        process = process_type(runner, item.widget().to_dict())
                        if not self.process_runner.run_process(process, item):
                            break
                else:  # https://www.geeksforgeeks.org/python-for-else/ (fucking crazy right??)
                    continue
                break
        # cleanup
        runner.set_directory(previous_directory)
        runner.set_number(previous_number)

    @staticmethod
    def directory_name():
        return "Loop"
