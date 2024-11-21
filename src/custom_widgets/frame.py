from PyQt6.QtWidgets import QFrame, QSizePolicy, QLayout
from typing import Callable


class Frame(QFrame):
    """QFrame that automatically sets the size policy and layout."""

    def __init__(self, layout_fn: Callable[[], QLayout], padding: int):
        """
        :param layout_fn: A function that returns a QLayout (i.e. **QVBoxLayout**, \
        not **QVBoxLayout()**)
        :param padding: The number of pixels to pad on each side.
        """
        super().__init__()

        self.setFrameStyle(QFrame.Shape.Box)

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = layout_fn()
        layout.setContentsMargins(padding, padding, padding, padding)
        self.setLayout(layout)
