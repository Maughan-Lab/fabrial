from .widgets import StabilityCheckWidget
from instruments import Oven, InstrumentSet  # ../instruments.py
from PyQt6.QtWidgets import QApplication
import sys


def test_widget_instatiation():
    """Test that a `StabilityCheckWidget` can be properly instantiated."""
    instruments = InstrumentSet(Oven("XXXX"), None)
    # need to create new QApplication before creating widgets
    app = QApplication(sys.argv)
    StabilityCheckWidget(instruments)
    app.quit()
