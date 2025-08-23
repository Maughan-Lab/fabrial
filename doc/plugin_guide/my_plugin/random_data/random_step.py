import random
import time
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

# the `StepRunner` class is how you interact with the GUI
from fabrial import SequenceStep, StepRunner

# fabrial's plotting module stores classes used for plotting
from fabrial.plotting import LineParams, PlotSettings, SymbolParams

# we import `NAME` so we always use the same "Random Data" string
from .random_widget import NAME
from .settings import PRINT_DATA_KEY, SETTINGS


class RandomDataStep(SequenceStep):
    """Record random data on an interval; step."""

    def __init__(self, data_interval: float):
        # we store this for later
        self.data_interval = data_interval

    # notice the `async def` on this function. `run()` must be
    # asynchronous, otherwise the step will not run. This is a
    # common mistake, so make sure you use `async def`!
    async def run(self, runner: StepRunner, data_directory: Path):
        # an `AsyncExitStack()` can have items added
        # to it during the context block
        async with AsyncExitStack() as exit_stack:
            plot_handle = await exit_stack.enter_async_context(
                runner.create_plot(
                    self, "A Random Plot", PlotSettings("Random Data", "Time (s)", "Value")
                )
            )
            # creating a plot does not automatically create a line
            # `add_line()` is asynchronous
            line_handle = await plot_handle.add_line(
                "The Data", LineParams("red", 3), SymbolParams("o", "blue", 5)
            )
            # we record the start time for plotting
            start_time = time.time()
            # `data_directory` is where our step should record data
            f = exit_stack.enter_context(open(data_directory.joinpath("random_data.txt"), "w"))
            for _ in range(20):  # we'll record 20 random data points
                data = random.random()
                f.write(f"{data}\n")
                # use the `add_point()` to plot new points
                line_handle.add_point(time.time() - start_time, data)
                # print the data to the terminal if printing is enabled
                if SETTINGS[PRINT_DATA_KEY]:
                    print(f"Random data! {data}")
                # `self.sleep()` pauses our step and lets the sequence
                # do something else. Notice the `await` keyword.
                # `self.sleep()` is also asynchronous, so this is the
                # syntax we use to call it. There is also
                # `self.sleep_until()` that you can use with
                # `time.time()`.
                await self.sleep(self.data_interval)
        # at the end of the block, `plot_handle` and `line_handle` or no longer valid

        # we can send a prompt to the user with `prompt_user()`.
        # It will show buttons based on the supplied dictionary,
        # and it will return an integer corresponding to the pressed
        # button (i.e. 0 for "Happy" and 1 for "Sad")
        response = await runner.prompt_user(
            self, "We finished! How do we feel?", {0: "Happy", 1: "Sad"}
        )
        match response:
            case 0:  # happy
                print("You feel happy")
            case 1:  # sad
                print("You feel sad")

    def reset(self):
        # our step doesn't have anything to "reset". If your step
        # accessed a physical device, for example, this function
        # would clean up and disconnect from that device
        pass  # do nothing

    def name(self) -> str:
        return NAME

    def metadata(self) -> dict[str, Any]:
        return {"Selected Data Interval": self.data_interval}
