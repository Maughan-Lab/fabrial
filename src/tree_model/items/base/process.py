from typing import Any
from ....classes.process import ProcessInputs


class BaseProcess:
    """
    Base class for all linked processes. You must override:
    - `run()`

    If you override `__init__()` make sure to call the base method.
    """

    def __init__(self, data: dict[str, Any]):
        """:param data: The data used to run this process."""
        self.data = data

    def run(self, inputs: ProcessInputs):
        """
        Run the process. When subclassing this method, you must ensure that long-running processes
        frequently call `time.sleep()`, otherwise they will freeze the application.

        :param inputs: A container with multiple useful inputs, such as application-wide instruments
        and the process runner's QThreadPool, which background processes can add themselves to.
        """
        pass
