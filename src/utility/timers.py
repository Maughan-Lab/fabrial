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
        super().__init__(parent)
        self.setInterval(intverval_ms)
        for slot in slots:
            self.timeout.connect(slot)

    def start_fast(self) -> Self:
        """Start the timer and instantly emit the timeout signal."""
        self.start()
        self.timeout.emit()
        return self


def new_timer(parent: QObject | None, interval_ms: int, *slots: Callable[[], Any]) -> QTimer:
    """
    Instantiate a new timer. **slots** are called immediately.

    :param parent: The QObject that owns this timer.
    :param interval_ms: The timeout in milliseconds.
    :param slots: The function(s) to connect the timer's timeout signal to.

    :returns: The created timer. The timer is already started. Note that you must keep a reference to the
    timer so it does not get deleted.
    """
    timer = Timer(parent, interval_ms, *slots)
    timer.start_fast()
    return timer
