# TODO: implement temperature sensor reading with PySerial
# import serial


class Oven:
    """Class to represent the physical oven Quincy controls."""

    def __init__(self, oven_port: str):
        pass

    def read_temp(self) -> float | None:
        """Returns the oven's temperature if the oven is connected, None otherwise."""
        pass

    def change_setpoint(self, setpoint: float):
        """Sets the oven's temperature to `setpoint`."""
        pass

    def get_setpoint(self) -> float | None:
        """Returns the oven's setpoint if the oven is connected, None otherwise."""
        pass
