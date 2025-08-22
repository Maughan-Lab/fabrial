from typing import Any

from .....classes import AbstractForegroundProcess, ProcessRunner
from .....instruments import Oven
from .....utility import dataframe
from ..set_temperature.encoding import SETPOINT
from ..set_temperature.process import SetTemperatureProcess
from . import encoding


class IncrementTemperatureProcess(SetTemperatureProcess):
    """Increment the oven's temperature and record data while waiting for it to stabilize."""

    def __init__(self, runner: ProcessRunner, data: dict[str, Any], name: str):
        data.update({SETPOINT: 0})
        SetTemperatureProcess.__init__(self, runner, data, name)

        self.increment = data[encoding.INCREMENT]

    @staticmethod
    def directory_name():
        return "Increment Temperature"

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
        SetTemperatureProcess.run(self)

    def title(self) -> str:  # overridden
        return f"Increment Temperature ({self.increment} °C)"

    def get_setpoint(self) -> tuple[float, bool]:
        """
        Get the oven's setpoint, going into an error state on failure. Retry until the read is
        successful.

        Returns
        -------
        A tuple of ([setpoint], [continue]). If [continue] is False, [setpoint] should be ignored.
        """
        setpoint = self.oven.get_setpoint()
        while setpoint is None:
            self.error_pause()
            if not self.wait(self.MEASUREMENT_INTERVAL, self.oven.is_connected):
                return (-1, False)
            setpoint = self.oven.get_setpoint()

        return (setpoint, True)

    def metadata(self):  # overridden
        return dataframe.add_to_dataframe(
            AbstractForegroundProcess.metadata(self), {"Selected Increment": self.increment}
        )
