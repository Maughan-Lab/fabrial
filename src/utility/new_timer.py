from PyQt6.QtCore import QTimer
from typing import Callable


def new_timer(interval_ms: int, slot: Callable[[], None]) -> QTimer:
    """
    Instantiate a new timer. **slot** is called immediately.

    :param interval_ms: The timeout interval of the timer in milliseconds.

    :param slot: The function to connect the timer's timeout signal to.
    :type slot: function

    :returns: The created timer. The timer is already started. Note that you must keep a reference to the
    timer so it does not get deleted.
    :rtype: QTimer
    """
    slot()
    timer = QTimer()
    timer.setInterval(interval_ms)
    timer.timeout.connect(slot)
    timer.start()
    return timer
