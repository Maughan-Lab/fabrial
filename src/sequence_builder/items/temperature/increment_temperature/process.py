from .....classes.process import Process
from ..set_temperature.process import SetTemperatureProcess
from ..set_temperature.encoding import SETPOINT
from .....classes.process_runner import ProcessRunner
from .....instruments import Oven
from typing import Any
from . import encoding
import polars as pl


class IncrementTemperatureProcess(SetTemperatureProcess):
    """Increment the oven's temperature and record data while waiting for it to stabilize."""

    DIRECTORY = "Increment Temperature"
    TITLE_PREFIX = "Increment Temperature"

    def __init__(self, runner: ProcessRunner, data: dict[str, Any]):  # overridden
        data.update({SETPOINT: 0})
        super().__init__(runner, data)

        self.increment = data[encoding.INCREMENT]

    def run(self):
        current_setpoint, proceed = self.get_setpoint()
        if not proceed:
            return
        setpoint, clamp_result = self.oven.clamp_setpoint(current_setpoint + self.increment)
        match clamp_result:
            case Oven.ClampResult.MAX_CLAMP | Oven.ClampResult.MIN_CLAMP:
                match clamp_result:
                    case Oven.ClampResult.MAX_CLAMP:
                        text = "Maximum"
                    case Oven.ClampResult.MIN_CLAMP:
                        text = "Minimum"
                self.communicate_error(f"{text} oven setpoint reached. The sequence will continue.")

        self.setpoint = setpoint
        super().run()

    def title(self) -> str:  # overridden
        return f"Increment Temperature ({self.increment} °C)"

    def metadata(self, end_time: float) -> pl.DataFrame:
        metadata = Process.metadata(self, end_time)
        metadata = pl.concat(
            [pl.DataFrame({"Selected Increment": self.increment}), metadata],
            how="horizontal",
        )
        return metadata

    def get_setpoint(self) -> tuple[float, bool]:
        """
        Get the oven's setpoint, going into an error state on failure. Retry until the read is
        successful.

        :returns: A tuple of ([setpoint], [continue]). If [continue] is False, [setpoint] should be
        ignored.
        """
        setpoint = self.oven.get_setpoint()
        if setpoint is None:
            self.error_pause()
            while setpoint is None:
                setpoint = self.oven.get_setpoint()
                if not self.wait(self.MEASUREMENT_INTERVAL, self.oven.is_connected):
                    return (-1, False)

        return (setpoint, True)
