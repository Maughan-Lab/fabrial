from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from instruments import Oven, InstrumentSet, ConnectionStatus
from stability_check.widgets import StabilityCheckWidget
from stability_check.stability_check import StabilityCheckThread
from sequence.widgets import SequenceWidget
from sequence.sequence import SequenceThread
from custom_widgets.spin_box import TemperatureSpinBox  # ../custom_widgets
from custom_widgets.groupbox import GroupBox
from utility.layouts import add_to_layout, add_sublayout  # ../utility
import file_locations
from sequence.constants import DATA_FILES_LOCATION
import sys
import os
import time

BASEDIR = os.path.dirname(__file__)
try:
    from ctypes import windll  # Only exists on Windows.

    myappid = "maughangroup.quincy.1"
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class DeveloperOven(Oven):
    def __init__(self, oven_port: str = ""):
        super().__init__(oven_port)
        self.unlocked = True
        self.developer_temperature = 0.0
        self.developer_setpoint = 0.0

    def set_connected(self, connection_status: ConnectionStatus):
        """Set the connection status and send signals."""
        self.update_connection_status(connection_status)

    def set_unlocked(self, unlocked: bool):
        """Set the unlocked status without firing signals."""
        self.unlocked = unlocked

    def set_temperature(self, temperature: float):
        """Set the oven's temperature."""
        self.developer_temperature = temperature

    # overridden methods

    # no need to override acquire() or release()

    # no need to override is_connected()

    def update_connection_status(self, connection_status: ConnectionStatus):
        self.connection_status = connection_status
        self.connectionChanged.emit(self.is_connected())

    def is_unlocked(self):
        """Return the previously set unlocked status."""
        return self.unlocked

    def read_temp(self) -> float | None:
        """Return the previously set temperature if connected, else None."""
        if self.is_connected():
            self.temperatureChanged.emit(self.developer_temperature)
            return self.developer_temperature
        else:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
            return None

    def change_setpoint(self, setpoint):
        """Set the setpoint."""
        self.developer_setpoint = setpoint
        if not self.is_connected():
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        return self.is_connected()

    def get_setpoint(self) -> float | None:
        if self.is_connected():
            self.setpointChanged.emit(self.developer_setpoint)
            return self.setpoint
        else:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        return None

    def connect(self):
        return

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
        self.create_freeze_widgets(layout)

    def create_connection_widgets(self, layout):
        connect_button = QPushButton("Connect")
        connect_button.pressed.connect(lambda: self.oven.set_connected(ConnectionStatus.CONNECTED))
        disconnect_button = QPushButton("Disconnect")
        disconnect_button.pressed.connect(
            lambda: self.oven.set_connected(ConnectionStatus.DISCONNECTED)
        )
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
        add_to_layout(add_sublayout(layout, QHBoxLayout), unlock_button, lock_button)

    def create_lock_signal_widgets(self, layout):
        acquire_button = QPushButton("Emit Acquired")
        acquire_button.pressed.connect(lambda: self.oven.lockChanged.emit(False))
        release_button = QPushButton("Emit Released")
        release_button.pressed.connect(lambda: self.oven.lockChanged.emit(True))
        add_to_layout(add_sublayout(layout, QHBoxLayout), release_button, acquire_button)

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

    def create_freeze_widgets(self, layout):
        freeze_button = QPushButton("Freeze for 10s")
        freeze_button.pressed.connect(self.freeze)
        add_to_layout(add_sublayout(layout, QHBoxLayout), freeze_button)

    def freeze(self):
        for i in range(1, 11):
            print(i)
            time.sleep(1)


class DeveloperMainWindow(MainWindow):
    """
    Add a DeveloperWidget for controlling the oven and use Developer versions of other widgets.
    """

    def __init__(self, instruments):
        super().__init__(instruments)
        layout = self.centralWidget().layout()
        layout.addWidget(DeveloperWidget(instruments), 0, 3)

    def initialize_widgets(self, instruments):
        """Use Developer versions of widgets."""
        super().initialize_widgets(instruments)
        # # reinitialize the oven's connection status to emit the proper signals
        # instruments.oven.connected = ConnectionStatus.NULL

        self.stability_check_widget = StabilityCheckWidget(
            instruments, DeveloperStabilityCheckThread
        )
        self.sequence_widget = SequenceWidget(instruments, DeveloperSequenceThread)


class DeveloperStabilityCheckThread(StabilityCheckThread):
    """Faster stabilization."""

    MEASUREMENT_INTERVAL = 1
    MINIMUM_MEASUREMENTS = 10


class DeveloperSequenceThread(SequenceThread):
    """Faster stabilization."""

    MEASUREMENT_INTERVAL = 1
    MINIMUM_MEASUREMENTS = 10


# --------------------------------------------------------------------------------------------------

FOLDERS_TO_CREATE = (file_locations.SAVED_SETTINGS_LOCATION, DATA_FILES_LOCATION)


def main():
    for folder in FOLDERS_TO_CREATE:
        os.makedirs(folder, exist_ok=True)
    # create instruments
    instruments = InstrumentSet(DeveloperOven(), None)
    # pass in any provided system arguments
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(file_locations.ICON_FILE))

    main_window = DeveloperMainWindow(instruments)
    main_window.show()

    app.exec()


if __name__ == "__main__":
    main()
