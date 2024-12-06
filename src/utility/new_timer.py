from PyQt6.QtCore import QTimer
from typing import Callable


def new_timer_nostart(interval_ms: int, slot: Callable[[], None]) -> QTimer:
    """
    Instantiate a new timer without starting it.

    :param interval_ms: The timeout interval of the timer in milliseconds.

    :param slot: The function to connect the timer's timeout signal to.
    :type slot: function

    :returns: The created timer. Note that you must keep a reference to the timer so it does not
    get deleted.
    """
    timer = QTimer()
    timer.setInterval(interval_ms)
    timer.timeout.connect(slot)
    return timer


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
    timer = new_timer_nostart(interval_ms, slot)
    slot()
    timer.start()
    return timer
