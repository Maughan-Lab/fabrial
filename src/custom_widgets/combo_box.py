from PyQt6.QtWidgets import QComboBox

MAX_VISIBLE_ITEMS = 20


class ComboBox(QComboBox):
    """QComboBox that doesn't show all entries at once."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("combobox-popup: 0")
        self.setMaxVisibleItems(MAX_VISIBLE_ITEMS)
