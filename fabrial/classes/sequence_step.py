from __future__ import annotations

import asyncio
import time
from abc import abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .step_runner import StepRunner


class SequenceStep(Protocol):
    """Represents a sequence step that the sequence can run."""

    @abstractmethod
    async def run(self, runner: StepRunner, data_directory: Path):
        """
        Run the sequence step. Ensure you call `self.sleep()` often enough that other tasks can be
        run.
        """
        ...

    @abstractmethod
    def reset(self):
        """
        Reset this step to its original state (i.e. before `run()` was called). Sequence steps might
        be re-used, so they must be resettable. An easy implementation is to call `__init__()` to
        reinitialize with the original parameters.
        """
        ...

    @abstractmethod
    def name(self) -> str:
        """A name used to represent this step. For example, "Hold" or "Increment Temperature"."""
        ...

    def directory_name(self) -> str:
        """
        Get the name (i.e. not full path) of the directory where data should be recorded. By default
        this just returns the result of `name()`.
        """
        return self.name()

    def metadata(self) -> dict[str, Any]:
        """
        Get metadata for this sequence step to be recorded in a JSON file. This is called after
        `run()` completes.
        """
        return {}

    async def sleep(self, delay: float):
        """
        Sleep this sequence step for **delay** seconds. This is *not* equivalent to `time.sleep()`
        and should be used *instead* of `time.sleep()`.

        Do not override this.
        """
        await asyncio.sleep(delay)

    async def sleep_until(self, when: float):
        """
        Sleep until **when**, which is a `float` as returned by `time.time()`.

        Do not override this.
        """
        await self.sleep(0)  # make sure we sleep at all
        await self.sleep(when - time.time())
