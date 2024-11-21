from PyQt6.QtCore import QRunnable, QObject, pyqtSignal, pyqtSlot
from instruments import InstrumentSet  # ../instruments.py
from enums.status import StabilityStatus  # ../enums
from time import time


# TODO: implement the stability check on this QRunnable
class StabilityCheckThread(QRunnable):
    """Thread for running stability checks."""

    # how far off the temperature can be from the setpoint for stability in degrees C
    ERROR_MARGIN = 1.0

    def __init__(self, instruments: InstrumentSet, setpoint: float):
        super().__init__()
        self.signals = Signals()

        self.setpoint = setpoint
        self.oven = instruments.oven
        self.cancel = False

    @pyqtSlot()
    def run(self):
        """Run a stability check in another thread."""
        self.pre_run()

        measurement_count = 0
        while measurement_count < 150:
            temperature = self.oven.read_temp()
            if temperature is None:
                self.update_stability(StabilityStatus.ERROR)
            else:
                if abs(temperature - self.setpoint) > self.ERROR_MARGIN:  # unstable
                    self.post_run(StabilityStatus.UNSTABLE)
                    return
                measurement_count += 1

            next_time = time() + 5
            while time() < next_time:  # wait 5 seconds
                if self.cancel:  # check to proceed
                    self.post_run(StabilityStatus.NULL)
                    return

        # if we make it here, we're stable!
        self.post_run(StabilityStatus.STABLE)

    def pre_run(self):
        """Pre-run tasks."""
        self.oven.aquire()
        self.signals.statusChanged.emit(True)
        self.update_stability(StabilityStatus.CHECKING)

    def post_run(self, final_stability: StabilityStatus):
        """Post-run tasks."""
        self.update_stability(final_stability)
        self.signals.statusChanged.emit(False)
        self.oven.release()

    def update_stability(self, stability: StabilityStatus):
        self.signals.stabilityChanged.emit(stability)

    def cancel_stability_check(self):
        self.cancel = True


class Signals(QObject):
    """Signals for the StabilityCheckThread."""

    stabilityChanged = pyqtSignal(StabilityStatus)
    statusChanged = pyqtSignal(bool)
