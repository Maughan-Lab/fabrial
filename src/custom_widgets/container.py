from PyQt6.QtWidgets import QWidget, QSizePolicy, QLayout
from typing import Callable


class Container(QWidget):
    """QWidget that automatically sets the size policy and layout."""

    def __init__(self, layout_fn: Callable[[], QLayout]):
        """
        :param layout_fn: A function that returns a QLayout (i.e. **QVBoxLayout**, \
        not **QVBoxLayout()**)
        """
        super().__init__()

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        layout = layout_fn()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
