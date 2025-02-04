from PyQt6.QtWidgets import QPushButton
from typing import Callable


class Button(QPushButton):
    """
    QPushButton that automatically connected any provided functions to the **pressed** signal.

    :param text: The text to display on the button.
    :param *push_fn: Function(s) to connect the **pressed** signal to.
    """

    def __init__(self, text: str, *push_fn: Callable[[], None]):
        super().__init__(text)
        for fn in push_fn:
            self.pressed.connect(fn)
