from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt


class Label(QLabel):
    """QLabel with the ability to select text."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
