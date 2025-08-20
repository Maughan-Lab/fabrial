## The Step

The step is what the sequence actually runs. Steps can do almost anything, and Fabrial provides tools for interacting with the user interface from a step. Steps use the [`SequenceStep`](../../fabrial/classes/sequence_step.py) protocol. Here are the imports and class definition:

<sub>Filename: random_data/random_step.py</sub>
```python
import random
import time
from pathlib import Path
from typing import Any

# the `StepRunner` class is how you interact with the GUI
from fabrial import SequenceStep, StepRunner

# we import `NAME` so we always use the same "Random Data" string
from .random_widget import NAME


class RandomDataStep(SequenceStep):
    """Record random data on an interval; step."""

    pass
```

`SequenceStep` requires the following methods:
- `async run()` - Called by the sequence to run the step. This is function is [asynchronous](https://docs.python.org/3/library/asyncio.html).
- `reset()` - Resets the sequence step to its original state, as if `run()` had never been called.
- `name()` - Provides a name for the step. For our step, this is the same as the widget's name.

Implementing them looks like:

<sub>Filename: random_data/random_step.py</sub>
```python
# --snip--

class RandomDataStep(SequenceStep):
    """Record random data on an interval; step."""

    def __init__(self, data_interval: float):
        # we store this for later
        self.data_interval = data_interval

    # notice the `async def` on this function. `run()` must be
    # asynchronous, otherwise the step will not run. This is a
    # common mistake, so make sure you use `async def`!
    async def run(self, runner: StepRunner, data_directory: Path):
        # `data_directory` is where our step should record data
        with open(data_directory.joinpath("random_data.txt"), "w") as f:
            for _ in range(20):  # we'll record 20 random data points
                data = random.random()
                f.write(f"{data}\n")
                # `self.sleep()` pauses our step and lets the sequence
                # do something else. Notice the `await` keyword.
                # `self.sleep()` is also asynchronous, so this is the
                # syntax we use to call it. There is also
                # `self.sleep_until()` that you can use with
                # `time.time()`.
                await self.sleep(self.data_interval)

    def reset(self):
        # our step doesn't have anything to "reset". If your step
        # accessed a physical device, for example, this function
        # would clean up and disconnect from that device
        pass  # do nothing

    def name(self) -> str:
        return NAME
```

There are some important things to note here. First, *`run()` must be `async`*. The sequence step will fail otherwise. Second, `reset()` must actually reset the step. `SequenceStep`s may be reused (as an example, the `Loop` step in the [core plugins](https://github.com/Maughan-Lab/fabrial-core-plugins) reuses steps), so failure to properly reset them will result in unpredictable behavior. Third, our step calls `self.sleep()` each time the loop runs. Without this, the sequence cannot multitask or receive commands from the user.

> #### `SequenceStep.sleep()` $\ne$ `time.sleep()`
> 
> `SequenceStep.sleep()` allows the sequence to multitask, while `time.sleep()` completely freezes the current thread. If you use `time.sleep()` instead of `SequenceStep.sleep()`, the sequence may become unresponsive. Using both together is fine.

`SequenceStep` also has the following optional methods:
- `directory_name()` - By default this just returns the result of `name()`. You can override this function if you want to store data in a differently-named directory.
- `metadata()` - Provides a dictionary of metadata to record. By default this returns an empty dictionary. This method is actually quite useful, since it allows you to extend the default metadata file. We'll implement it later on.

___

All right! Our step is now functional. We'll expand its capabilities shortly, but for now we should check that it works.

The complete step code is shown below.

<sub>Filename: random_data/random_step.py</sub>
```python
import random
from pathlib import Path

from fabrial import SequenceStep, StepRunner

from .random_widget import NAME


class RandomDataStep(SequenceStep):
    """Record random data on an interval; step."""

    def __init__(self, data_interval: float):
        self.data_interval = data_interval

    async def run(self, runner: StepRunner, data_directory: Path):
        with open(data_directory.joinpath("random_data.txt"), "w") as f:
            for _ in range(20):
                data = random.random()
                f.write(f"{data}\n")
                await self.sleep(self.data_interval)

    def reset(self):
        pass

    def name(self) -> str:
        return NAME
```