from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot, QRunnable
from ..instruments import INSTRUMENTS, InstrumentLocker
from ..enums.status import StabilityStatus
import time


class StabilityCheckThread(QRunnable):
    """Thread for running stability checks."""

    MINIMUM_MEASUREMENTS = 150
    VARIANCE_TOLERANCE = 1.0  # degree C
    MEASUREMENT_INTERVAL = 5  # seconds
    WAIT_INTERVAL = 0.01  # seconds

    def __init__(self, setpoint: float):
        super().__init__()
        # signals
        self.signals = Signals()

        self.setpoint = setpoint
        self.oven = INSTRUMENTS.oven
        self.cancel = False
        self.connection_problem = False

    @pyqtSlot()
    def run(self):
        """Run a stability check in another thread."""
        with InstrumentLocker(self.oven):
            self.pre_run()
            final_stability = StabilityStatus.STABLE

            measurement_count = 0
            while True:
                temperature = self.oven.read_temp()
                if temperature is None:
                    self.process_connection_problem()
                else:
                    if abs(temperature - self.setpoint) > self.VARIANCE_TOLERANCE:  # unstable
                        final_stability = StabilityStatus.UNSTABLE
                        break
                    measurement_count += 1
                    self.signals.progressed.emit()
                    if measurement_count >= self.MINIMUM_MEASUREMENTS:
                        break  # end the sequence

                proceed = self.wait()
                if not proceed:
                    final_stability = StabilityStatus.NULL
                    break

            # if we make it here, we're stable!
            self.post_run(final_stability)

    def pre_run(self):
        """Pre-run tasks."""
        self.signals.statusChanged.emit(True)
        self.update_stability(StabilityStatus.CHECKING)

    def post_run(self, final_stability: StabilityStatus):
        """Post-run tasks."""
        self.update_stability(final_stability)
        self.signals.statusChanged.emit(False)

    def wait(self) -> bool:
        """Wait for **MEASUREMENT_INTERVAL** and handle connection problems."""
        end_time = time.time() + self.MEASUREMENT_INTERVAL
        while time.time() < end_time or self.connection_problem:
            if self.cancel:
                return False
            if self.connection_problem:
                if self.oven.is_connected():
                    self.connection_problem = False
                    self.update_stability(StabilityStatus.CHECKING)
            time.sleep(self.WAIT_INTERVAL)
        return True

    def process_connection_problem(self):
        self.connection_problem = True
        self.update_stability(StabilityStatus.ERROR)

    def update_stability(self, stability: StabilityStatus):
        self.signals.stabilityChanged.emit(stability)

    def cancel_stability_check(self):
        self.cancel = True


class Signals(QObject):
    stabilityChanged = pyqtSignal(StabilityStatus)
    statusChanged = pyqtSignal(bool)
    progressed = pyqtSignal()
