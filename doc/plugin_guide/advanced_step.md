## Expanding Our Sequence Step

### Communicating With the GUI

Let's add some import sand modify our step's `run()` method to interact with the GUI. Using the `StepRunner` that gets passed to `run()`, we can plot data in real time and send prompts to the user.

<sub>Filename: random_data/random_step.py</sub>
```python
# --snip--

# fabrial's plotting module stores classes used for plotting
from fabrial.plotting import LineParams, PlotSettings, SymbolParams

# --snip--

    async def run(self, runner: StepRunner, data_directory: Path):
        # `create_plot()` is an asynchronous context manager,
        # so it uses an `async with` block
        async with runner.create_plot(
            self, "A Random Plot", PlotSettings("Random Data", "Time (s)", "Value")
        ) as plot_handle:
            # creating a plot does not automatically create a line
            # `add_line()` is asynchronous
            line_handle = await plot_handle.add_line(
                LineSettings("The Data", "red", 3, "o", "blue", 5)
            )
            # we record the start time for plotting
            start_time = time.time()
            with open(data_directory.joinpath("random_data.txt"), "w") as f:
                for _ in range(20):  # we'll record 20 random data points
                    data = random.random()
                    f.write(f"{data}\n")
                    # use the `add_point()` to plot new points
                    line_handle.add_point(time.time() - start_time, data)
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

    # --snip--
```

If you run a sequence with these changes, you should see real-time plotting in the visuals tab. When the sequence step completes, it should show you a Happy/Sad prompt. Selecting an option will print a message to the terminal.

> Since it's such a common case, the `StepRunner` also provides the `prompt_retry_cancel()` method. It will prompt the user to retry something or cancel the calling step. If the user chooses the cancel option, `prompt_retry_cancel()` will raise a `StepCancellation` exception.

> #### Note
> 
> For plotting, plot handles and line handles are only valid inside the `async with` block. Using them after the block ends is a fatal error.

### Adding More Metadata

The `SequenceStep`'s `metadata()` method can be overridden to record extra metadata. For example, we can record the data interval the user selected.

<sub>Filename: random_data/random_step.py</sub>
```python
    # --snip--

    def name(self) -> str:  # no change here
        return NAME

    def metadata(self) -> dict[str, Any]:
        return {"Selected Data Interval": self.data_interval}
```

If you run a sequence with this change, our step's metadata file will have an entry called `Selected Data Interval`.

___

This is pretty much all directly Fabrial exposes for customization. However, `SequenceStep`s have an enormous amount of flexibility; most of what you'd want to accomplish can implemented using `run()`.

The complete step code is shown below (cleaned up a bit using an [`AsyncExitStack`](https://docs.python.org/3/library/contextlib.html#contextlib.AsyncExitStack)).

<sub>Filename: random_data/random_step.py</sub>
```python
import random
import time
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from fabrial import SequenceStep, StepRunner
from fabrial.plotting import LineParams, PlotSettings, SymbolParams

from .random_widget import NAME


class RandomDataStep(SequenceStep):
    """Record random data on an interval; step."""

    def __init__(self, data_interval: float):
        self.data_interval = data_interval

    async def run(self, runner: StepRunner, data_directory: Path):
        # an `AsyncExitStack()` can have items added
        # to it during the context block
        async with AsyncExitStack() as exit_stack:
            plot_handle = await exit_stack.enter_async_context(
                runner.create_plot(
                    self, "A Random Plot", PlotSettings("Random Data", "Time (s)", "Value")
                )
            )
            line_handle = await plot_handle.add_line(
                "The Data", LineParams("red", 3), SymbolParams("o", "blue", 5)
            )
            start_time = time.time()
            f = exit_stack.enter_context(open(data_directory.joinpath("random_data.txt"), "w"))
            for _ in range(20):
                data = random.random()
                f.write(f"{data}\n")
                line_handle.add_point(time.time() - start_time, data)
                await self.sleep(self.data_interval)

        response = await runner.prompt_user(
            self, "We finished! How do we feel?", {0: "Happy", 1: "Sad"}
        )
        match response:
            case 0:
                print("You feel happy")
            case 1:
                print("You feel sad")

    def reset(self):
        pass

    def name(self) -> str:
        return NAME

    def metadata(self) -> dict[str, Any]:
        return {"Selected Data Interval": self.data_interval}

```