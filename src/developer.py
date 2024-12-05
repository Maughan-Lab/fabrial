from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QPushButton,
)
from main_window import MainWindow
from instruments import Oven, InstrumentSet
from stability_check.widgets import StabilityCheckWidget
from stability_check.stability_check import StabilityCheckProcess
from sequence.widgets import SequenceWidget
from sequence.sequence import SequenceProcess
import sys
import os
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from utility.layouts import add_to_layout, add_sublayout  # ../utility

BASEDIR = os.path.dirname(__file__)
try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "maughangroup.quincy.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class DeveloperOven(Oven):
    def __init__(self, oven_port):
        super().__init__(oven_port)
        self.unlocked = True
        self.temperature = 0.0
        self.setpoint = 0.0

    def set_connected(self, conntected: bool):
        """Set the connection status without firing signals."""
        self.connected = conntected

    def set_unlocked(self, unlocked: bool):
        """Set the unlocked status without firing signals."""
        self.unlocked = unlocked

    def set_temperature(self, temperature: float):
        """Set the oven's temperature."""
        self.temperature = temperature

    # overridden methods
    def acquire(self):
        """Emits the lockChanged(False) signal."""
        self.lockChanged.emit(False)

    def release(self):
        """Emits the lockChanged(True) signal."""
        self.lockChanged.emit(True)

    # no need to override is_connected()

    def is_unlocked(self):
        """Return the previously set unlocked status."""
        return self.unlocked

    def read_temp(self) -> float | None:
        """Return the previously set temperature if connected, else None."""
        if self.connected:
            return self.temperature
        else:
            return None

    def change_setpoint(self, setpoint):
        """Set the setpoint."""
        self.setpoint = setpoint

    def get_setpoint(self) -> float | None:
        """Return the previously set setpoint if connected, else None."""
        if self.is_connected():
            return self.setpoint
        else:
            return None

    def connect(self):
        """Do nothing."""
        pass

    def update_port(self, port):
        """Update the port variable and do nothing else."""
        self.port = port
        pass


class DeveloperWidget(GroupBox):
    def __init__(self, instruments: InstrumentSet):
        super().__init__("Developer", QVBoxLayout, instruments)
        self.oven = instruments.oven
        layout = self.layout()
        self.create_connection_widgets(layout)
        self.create_connection_signal_widgets(layout)
        self.create_lock_widgets(layout)
        self.create_lock_signal_widgets(layout)
        self.create_temperature_widgets(layout)
        self.create_setpoint_widgets(layout)

    def create_connection_widgets(self, layout):
        connect_button = QPushButton("Connect")
        connect_button.pressed.connect(lambda: self.oven.set_connected(True))
        disconnect_button = QPushButton("Disconnect")
        disconnect_button.pressed.connect(lambda: self.oven.set_connected(False))
        add_to_layout(add_sublayout(layout, QHBoxLayout), connect_button, disconnect_button)

    def create_connection_signal_widgets(self, layout):
        connected_button = QPushButton("Emit Connected")
        connected_button.pressed.connect(lambda: self.oven.connectionChanged.emit(True))
        disconnected_button = QPushButton("Emit Disconnect")
        disconnected_button.pressed.connect(lambda: self.oven.connectionChanged.emit(False))
        add_to_layout(add_sublayout(layout, QHBoxLayout), connected_button, disconnected_button)

    def create_lock_widgets(self, layout):
        lock_button = QPushButton("Lock")
        lock_button.pressed.connect(lambda: self.oven.set_unlocked(False))
        unlock_button = QPushButton("Unlock")
        unlock_button.pressed.connect(lambda: self.oven.set_unlocked(True))
        add_to_layout(add_sublayout(layout, QHBoxLayout), lock_button, unlock_button)

    def create_lock_signal_widgets(self, layout):
        acquire_button = QPushButton("Emit Acquired")
        acquire_button.pressed.connect(self.oven.acquire)
        release_button = QPushButton("Emit Released")
        release_button.pressed.connect(self.oven.release)
        add_to_layout(add_sublayout(layout, QHBoxLayout), acquire_button, release_button)

    def create_temperature_widgets(self, layout):
        temperature_spinbox = TemperatureSpinBox()
        temperature_spinbox.lineEdit().returnPressed.connect(
            lambda: self.oven.set_temperature(temperature_spinbox.value())
        )
        temperature_button = QPushButton("Change Temperature")
        temperature_button.pressed.connect(
            lambda: self.oven.set_temperature(temperature_spinbox.value())
        )
        add_to_layout(add_sublayout(layout, QHBoxLayout), temperature_spinbox, temperature_button)

    def create_setpoint_widgets(self, layout):
        setpoint_spinbox = TemperatureSpinBox()
        setpoint_spinbox.lineEdit().returnPressed.connect(
            lambda: self.oven.change_setpoint(setpoint_spinbox.value())
        )
        setpoint_button = QPushButton("Change Setpoint")
        setpoint_button.pressed.connect(lambda: self.oven.change_setpoint(setpoint_spinbox.value()))
        add_to_layout(add_sublayout(layout, QHBoxLayout), setpoint_spinbox, setpoint_button)


class DeveloperMainWindow(MainWindow):
    def __init__(self, instruments):
        super().__init__(instruments)
        layout: QGridLayout = self.centralWidget().layout()
        layout.addWidget(DeveloperWidget(instruments), 0, 3)


class DeveloperStabilityCheckWidget(StabilityCheckWidget):
    def __init__(self, instruments):
        super().__init__(instruments)

    def start_stability_check(self):
        return super().start_stability_check()


def main():
    # create instruments
    instruments = InstrumentSet(DeveloperOven("XXXX"), None)
    # pass in any provided system arguments
    app = QApplication(sys.argv)

    main_window = DeveloperMainWindow(instruments)
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()
