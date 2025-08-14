from typing import Iterable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QComboBox

MAX_VISIBLE_ITEMS = 20


class ComboBox(QComboBox):
    """QComboBox that doesn't show all entries at once."""

    # signal to detect when the combobox is pressed
    pressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        QComboBox.__init__(self, *args, **kwargs)
        self.setStyleSheet("combobox-popup: 0")
        self.setMaxVisibleItems(MAX_VISIBLE_ITEMS)

    def setCurrentIndexSilent(self, index: int):
        """Update the current index without emitting signals."""
        self.blockSignals(True)
        self.setCurrentIndex(index)
        self.blockSignals(False)

    def setCurrentTextSilent(self, text: str | None):
        """Update the current text without emitting signals."""
        self.blockSignals(True)
        self.setCurrentText(text)
        self.blockSignals(False)

    def clearSilent(self):
        """Clear the combobox entries without emitting signals."""
        self.blockSignals(True)
        self.clear()
        self.blockSignals(False)

    def addItemsSilent(self, items: Iterable[str | None]):
        """Add items to the combobox without emitting signals."""
        self.blockSignals(True)
        self.addItems(items)
        self.blockSignals(False)

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def showPopup(self):
        self.pressed.emit()
        QComboBox.showPopup(self)
