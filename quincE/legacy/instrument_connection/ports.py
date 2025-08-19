from serial.tools import list_ports as ports_util


def list_ports() -> list[str]:
    """Returns a list of available system com ports from pyserial."""
    ports: list[str] = []
    # serial.tools.list_ports.comports() returns a list of ports
    for port_info in ports_util.comports():
        # .device accesses the name of the port, i.e. /dev/ttyS14 on Linux or COM5 on windows
        ports.append(port_info.device)
    return ports
