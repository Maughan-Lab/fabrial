from PyQt6.QtWidgets import QGroupBox, QLayout, QSizePolicy


class Frame(QGroupBox):
    """QFrame that automatically sets the size policy and layout."""

    def __init__(self, layout: QLayout, padding: int = 0):
        """
        :param layout: The layout.
        :param padding: The number of pixels to pad on each side.
        """
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout.setContentsMargins(padding, padding, padding, padding)
        self.setLayout(layout)
