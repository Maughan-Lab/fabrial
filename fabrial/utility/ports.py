from serial.tools import list_ports as ports_util


def list_ports() -> list[str]:
    """
    Get a list of available ports.

    # Returns
    A list of available port strings (i.e. "COM4" on Windows or "/dev/ttyUSB0" on
    Linux).
    """
    return [port_info.device for port_info in ports_util.comports()]
