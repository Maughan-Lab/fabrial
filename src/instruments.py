from dataclasses import dataclass
from temperature_sensor import Oven


@dataclass
class InstrumentSet:
    """Container for instruments (the oven, potentiostats, etc.)"""

    oven: Oven
    potentiostat: None
