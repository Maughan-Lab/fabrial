from typing import Any, Callable, Self

from PyQt6.QtCore import QObject, QTimer


class Timer(QTimer):
    """Easier QTimer class."""

    def __init__(self, parent: QObject | None, intverval_ms: int, *slots: Callable[[], Any]):
        """
        Instantiate a new timer and automatically connect the passed in **slots**.

        :param parent: The QObject that owns this timer.
        :param interval_ms: The timeout interval in milliseconds.
        :param slots: Function(s) to call when the timer times out.
        """
        QTimer.__init__(self, parent)
        self.setInterval(intverval_ms)
        for slot in slots:
            self.timeout.connect(slot)

    def start_fast(self) -> Self:
        """Start the timer and instantly emit the timeout signal."""
        self.start()
        self.timeout.emit()
        return self
