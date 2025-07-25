from PyQt6.QtWidgets import QGroupBox, QLayout, QSizePolicy


class GroupBox(QGroupBox):
    """QGroupBox with that automatically sets the SizePolicy and title."""

    def __init__(self, title: str | None, layout: QLayout):
        """
        :param title: The window's title.
        :param layout: The layout to initialize with.
        """
        QGroupBox.__init__(self)
        self.setTitle(title)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setLayout(layout)
