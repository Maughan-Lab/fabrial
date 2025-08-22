from typing import Any

from .....classes import AbstractForegroundProcess, ProcessRunner
from .....utility import dataframe
from . import encoding


class LoopProcess(AbstractForegroundProcess):
    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        AbstractForegroundProcess.__init__(self, runner, data, name)
        self.number_of_loops = data[encoding.NUMBER_OF_LOOPS]
        self.loops_completed = 0

    def run(self) -> None:
        # reconfigure the runner while saving previous values
        runner = self.runner()
        previous_directory = runner.directory()
        previous_number = runner.number()
        runner.set_directory(self.directory())
        runner.reset_number()

        # run each item and repeat for the loop number
        loop_item = runner.current_item()
        if loop_item is not None:
            while self.loops_completed < self.number_of_loops:
                for item in loop_item.subitems():
                    process_type = item.process_type()
                    if process_type is not None:
                        widget = item.widget()
                        process = process_type(runner, widget.to_dict(), widget.display_name())
                        if not self.process_runner.run_process(process, item):
                            break
                else:  # https://www.geeksforgeeks.org/python-for-else/ (fucking crazy right??)
                    self.loops_completed += 1
                    continue
                break
        # cleanup
        runner.set_directory(previous_directory)
        runner.set_number(previous_number)

    @staticmethod
    def directory_name():
        return "Loop"

    def metadata(self):
        return dataframe.add_to_dataframe(
            AbstractForegroundProcess.metadata(self),
            {
                "Selected Loop Count": self.number_of_loops,
                "Actual Loops Completed": self.loops_completed,
            },
        )
