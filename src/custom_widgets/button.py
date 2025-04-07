from PyQt6.QtWidgets import QPushButton, QSizePolicy
from typing import Callable


class Button(QPushButton):
    """QPushButton that automatically connected any provided functions to the **pressed** signal."""

    def __init__(self, text: str, *push_fn: Callable[[], None]):
        """
        :param text: The text to display on the button.
        :param push_fn: Function(s) to connect the **pressed** signal to.
        """
        super().__init__(text)
        for fn in push_fn:
            self.pressed.connect(fn)


class FixedButton(Button):
    """
    Button with a fixed size.
    """

    def __init__(self, text: str, *push_fn: Callable[[], None]):
        super().__init__(text, *push_fn)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
