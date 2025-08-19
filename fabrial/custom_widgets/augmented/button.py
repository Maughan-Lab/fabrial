from typing import Any, Callable

from PyQt6.QtCore import QSize
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

        Parameters
        ----------
        size_scalars
            The new vertical and horizontal (respectively) size scalars.
        """
        self.horizontal_scalar, self.vertical_scalar = size_scalars

    def sizeHint(self) -> QSize:  # overridden
        default_size = Button.sizeHint(self)
        return QSize(
            round(default_size.width() * self.horizontal_scalar),
            round(default_size.height() * self.vertical_scalar),
        )
