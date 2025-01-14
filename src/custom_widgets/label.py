from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt


class Label(QLabel):
    """QLabel with adaptive size and the ability to select text."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
