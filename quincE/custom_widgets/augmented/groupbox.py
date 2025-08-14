from PyQt6.QtWidgets import QGroupBox, QLayout, QSizePolicy


class GroupBox(QGroupBox):
    """
    `QGroupBox` with that automatically sets the size policy and title.

    Parameters
    ----------
    title
        The window's title.
    layout
        The layout to initialize with.
    """

    def __init__(self, title: str | None, layout: QLayout):
        QGroupBox.__init__(self)
        self.setTitle(title)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setLayout(layout)
