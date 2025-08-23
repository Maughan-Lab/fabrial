"""Uses a fake oven to simulate reading temperatures."""

import time

from PyQt6.QtWidgets import QHBoxLayout, QPushButton, QVBoxLayout

from fabrial import MainWindow
from fabrial.custom_widgets import GroupBox, TemperatureSpinBox
from fabrial.legacy.instruments import INSTRUMENTS, ConnectionStatus, Oven
from fabrial.__main__ import main
from fabrial.utility import layout as layout_util


class DeveloperOven(Oven):
    def __init__(self):
        Oven.__init__(self)
        self.unlocked = True
        self.developer_temperature = 0.0
        self.developer_setpoint = 0.0
        self.set_connected(ConnectionStatus.CONNECTED)
        self.set_unlocked(True)

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
            self.update_temperature(self.developer_temperature)
            return self.developer_temperature
        else:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
            return None

    def change_setpoint(self, setpoint):
        """Set the setpoint."""
        self.developer_setpoint = setpoint
        if not self.is_connected():
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        else:
            self.update_setpoint(setpoint)
            self.reset_stability()
        return self.is_connected()

    def get_setpoint(self) -> float | None:
        if self.is_connected():
            self.update_setpoint(self.developer_setpoint)
            return self.developer_setpoint
        else:
            self.update_connection_status(ConnectionStatus.DISCONNECTED)
        return None

    def connect(self):
        return

    def set_port(self, port):
        """Update the port variable and do nothing else."""
        self.port = port
        pass


class DeveloperWidget(GroupBox):
    def __init__(self):
        layout = QVBoxLayout()
        GroupBox.__init__(self, "Developer", layout)
        self.oven = INSTRUMENTS.oven
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
        layout_util.add_to_layout(
            layout_util.add_sublayout(layout, QHBoxLayout), connect_button, disconnect_button
        )

    def create_connection_signal_widgets(self, layout):
        connected_button = QPushButton("Emit Connected")
        connected_button.pressed.connect(lambda: self.oven.connectionChanged.emit(True))
        disconnected_button = QPushButton("Emit Disconnect")
        disconnected_button.pressed.connect(lambda: self.oven.connectionChanged.emit(False))
        layout_util.add_to_layout(
            layout_util.add_sublayout(layout, QHBoxLayout), connected_button, disconnected_button
        )

    def create_lock_widgets(self, layout):
        lock_button = QPushButton("Lock")
        lock_button.pressed.connect(lambda: self.oven.set_unlocked(False))
        unlock_button = QPushButton("Unlock")
        unlock_button.pressed.connect(lambda: self.oven.set_unlocked(True))
        layout_util.add_to_layout(
            layout_util.add_sublayout(layout, QHBoxLayout), unlock_button, lock_button
        )

    def create_lock_signal_widgets(self, layout):
        acquire_button = QPushButton("Emit Acquired")
        acquire_button.pressed.connect(lambda: self.oven.lockChanged.emit(False))
        release_button = QPushButton("Emit Released")
        release_button.pressed.connect(lambda: self.oven.lockChanged.emit(True))
        layout_util.add_to_layout(
            layout_util.add_sublayout(layout, QHBoxLayout), release_button, acquire_button
        )

    def create_temperature_widgets(self, layout):
        temperature_spinbox = TemperatureSpinBox(INSTRUMENTS.oven)
        temperature_spinbox.lineEdit().returnPressed.connect(
            lambda: self.oven.set_temperature(temperature_spinbox.value())
        )
        temperature_button = QPushButton("Change Temperature")
        temperature_button.pressed.connect(
            lambda: self.oven.set_temperature(temperature_spinbox.value())
        )
        layout_util.add_to_layout(
            layout_util.add_sublayout(layout, QHBoxLayout), temperature_spinbox, temperature_button
        )

    def create_setpoint_widgets(self, layout):
        setpoint_spinbox = TemperatureSpinBox(INSTRUMENTS.oven)
        setpoint_spinbox.lineEdit().returnPressed.connect(
            lambda: self.oven.change_setpoint(setpoint_spinbox.value())
        )
        setpoint_button = QPushButton("Change Setpoint")
        setpoint_button.pressed.connect(lambda: self.oven.change_setpoint(setpoint_spinbox.value()))
        layout_util.add_to_layout(
            layout_util.add_sublayout(layout, QHBoxLayout), setpoint_spinbox, setpoint_button
        )

    def create_freeze_widgets(self, layout):
        freeze_button = QPushButton("Freeze for 10s")
        freeze_button.pressed.connect(self.freeze)
        layout_util.add_to_layout(layout_util.add_sublayout(layout, QHBoxLayout), freeze_button)

    def freeze(self):
        for i in range(1, 11):
            print(i)
            time.sleep(1)


class DeveloperMainWindow(MainWindow):
    """
    Add a DeveloperWidget for controlling the oven and use Developer versions of other widgets.
    """

    def __init__(self) -> None:
        MainWindow.__init__(self)
        layout: QHBoxLayout = self.oven_control_tab.layout().itemAt(0).layout()  # type: ignore
        layout.addWidget(DeveloperWidget())


# --------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    INSTRUMENTS.oven = DeveloperOven()
    main(DeveloperMainWindow)
