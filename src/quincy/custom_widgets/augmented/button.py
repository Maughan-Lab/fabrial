from typing import Any, Callable

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QPushButton, QSizePolicy


class Button(QPushButton):
    """QPushButton that automatically connected any provided functions to the **pressed** signal."""

    def __init__(self, text: str, *push_fn: Callable[[], None | Any]):
        """
        :param text: The text to display on the button.
        :param push_fn: Function(s) to connect the **pressed** signal to.
        """
        QPushButton.__init__(self, text)
        for fn in push_fn:
            self.clicked.connect(fn)


class FixedButton(Button):
    """
    Button with a fixed size.
    """

    def __init__(self, text: str, *push_fn: Callable[[], None | Any]):
        Button.__init__(self, text, *push_fn)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)


class BiggerButton(Button):  # this name feels so dumb xD
    """Button with user-selected size scaling."""

    def __init__(
        self,
        text: str,
        *push_fn: Callable[[], None | Any],
        size_scalars: tuple[float, float] = (1, 1),
    ):
        Button.__init__(self, text, *push_fn)
        self.horizontal_scalar, self.vertical_scalar = size_scalars

    def set_size_scalars(self, size_scalars: tuple[float, float]):
        """
        Set the vertical and horizontal size scalars.

        :param size_scalars: The new vertical and horizontal (respectively) size scalars.
        """
        self.horizontal_scalar, self.vertical_scalar = size_scalars

    # overridden method
    def sizeHint(self):
        default_size = Button.sizeHint(self)
        return QSize(
            round(default_size.width() * self.horizontal_scalar),
            round(default_size.height() * self.vertical_scalar),
        )
