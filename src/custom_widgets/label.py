from PyQt6.QtWidgets import QLabel, QFormLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from .container import Container
from typing import Self


class Label(QLabel):
    """QLabel with the ability to select text."""

    def __init__(self, text: str = ""):
        super().__init__(text)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def set_color(self, color: str) -> Self:
        """Set the label's text color. Supports color names, like "blue" or "lightgreen"."""
        self.setStyleSheet("color: " + color)
        return self


class IconLabel(Container):
    """Label with an icon on the left. Both are contained in a Container (this widget)."""

    def __init__(self, icon: QPixmap, text: str = ""):
        layout = QFormLayout()
        super().__init__(layout)

        self.icon_label = QLabel()
        self.icon_label.setPixmap(icon)
        self.text_label = Label(text)

        layout.addRow(self.icon_label, self.text_label)

    def label(self) -> Label:
        """Get the text label."""
        return self.text_label

    def pixmap(self) -> QPixmap:
        """Get the pixmap."""
        return self.icon_label.pixmap()
