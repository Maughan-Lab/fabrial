from PyQt6.QtWidgets import QGroupBox, QSizePolicy, QLayout
from ..instruments import InstrumentSet
from typing import Callable


class GroupBox(QGroupBox):
    """QGroupBox with that automatically sets the SizePolicy and title and assigns instruments."""

    def __init__(
        self, title: str | None, layout_fn: Callable[[], QLayout], instruments: InstrumentSet
    ):
        """
        :param title: The window's title.
        :param layout_fn: A function that returns a QLayout (i.e. **QVBoxLayout**, \
        not **QVBoxLayout()**)
        :param instruments: The instruments used by the widget.
        """
        super().__init__()
        self.setTitle(title)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.instruments = instruments
        self.setLayout(layout_fn())
