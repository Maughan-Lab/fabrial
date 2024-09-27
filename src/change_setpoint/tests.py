from .widgets import SetTempWidget
from temperature_sensor import Oven
from PyQt6.QtWidgets import QApplication
import sys


def test_widget_instatiation():
    """Test that a SetTemptWidget can be properly instantiated."""
    oven = Oven("XXXX")
    # need to create new QApplication before creating widgets
    app = QApplication(sys.argv)
    SetTempWidget(oven)
    app.quit()
