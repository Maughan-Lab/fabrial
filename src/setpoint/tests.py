from .widgets import SetpointWidget
from temperature_sensor import Oven
from instruments import InstrumentSet  # ../instruments.py
from PyQt6.QtWidgets import QApplication
import sys


def test_widget_instatiation():
    """Test that a SetTemptWidget can be properly instantiated."""
    instruments = InstrumentSet(Oven("XXXX"), None)
    # need to create new QApplication before creating widgets
    app = QApplication(sys.argv)
    SetpointWidget(instruments)
    app.quit()
