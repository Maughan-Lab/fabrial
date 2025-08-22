from collections.abc import Callable
from typing import Any, Self

from PyQt6.QtCore import QObject, QTimer


class Timer(QTimer):
    """
    Easier QTimer class. The passes in **slots** are automatically connected to the `timeout`
    signal.

    Parameters
    ----------
    parent
        The QObject that owns this timer.
    interval_ms
        The timeout interval in milliseconds.
    slots
        Function(s) to call when the timer times out.
    """

    def __init__(self, parent: QObject | None, intverval_ms: int, *slots: Callable[[], Any]):
        QTimer.__init__(self, parent)
        self.setInterval(intverval_ms)
        for slot in slots:
            self.timeout.connect(slot)

    def start_fast(self) -> Self:
        """Start the timer and instantly emit the timeout signal."""
        self.start()
        self.timeout.emit()
        return self
