from PyQt6.QtWidgets import QComboBox
from PyQt6.QtCore import pyqtSignal

MAX_VISIBLE_ITEMS = 20


class ComboBox(QComboBox):
    """QComboBox that doesn't show all entries at once."""

    # signal to detect when the combobox is pressed
    pressed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    # ----------------------------------------------------------------------------------------------
    # overridden methods
    def showPopup(self):
        self.pressed.emit()
        super().showPopup()
