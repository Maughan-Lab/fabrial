# TODO: implement temperature sensor reading with PySerial
# import serial


class Oven:
    """Class to represent the physical oven Quincy controls."""

    def __init__(self, oven_port: str):
        self.port = oven_port
        self.connected = self.connect()

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if the oven is connected, None otherwise."""
        if self.connected:
            return 1  # TODO: implement actually reading the temperature
        else:
            return None

    def change_setpoint(self, setpoint: float):
        """Sets the oven's temperature to `setpoint`."""
        pass

    def get_setpoint(self) -> float | None:
        """Returns the oven's setpoint if the oven is connected, None otherwise."""
        if self.connected:
            return 1  # TODO: implement actually reading the setpoint
        else:
            return None

    def connect(self):
        """Attempts to connect to the oven. A failed attempt will set `connected` to False."""
        # TODO: implement the connection
        self.connected = False

    def update_port(self, port: str):
        """Updates the oven's connection port."""
        self.port = port
