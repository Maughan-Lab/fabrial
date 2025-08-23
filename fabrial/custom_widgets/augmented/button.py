from collections.abc import Callable
from typing import Any

from PyQt6.QtWidgets import QPushButton, QSizePolicy


class Button(QPushButton):
    """
    `QPushButton` that automatically connects any provided functions to the `clicked` signal.

    Parameters
    ----------
    text
        The text to display on the button.
    push_fn
        Function(s) to connect the `clicked` signal to.
    """

    def __init__(self, text: str, *push_fn: Callable[[], None | Any]):
        QPushButton.__init__(self, text)
        for fn in push_fn:
            self.clicked.connect(fn)


class FixedButton(Button):
    """Button with a fixed size."""

    def __init__(self, text: str, *push_fn: Callable[[], None | Any]):
        Button.__init__(self, text, *push_fn)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
