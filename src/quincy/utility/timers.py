from typing import Any, Callable

from PyQt6.QtCore import QObject

from ..classes.timer import Timer


def new_timer(parent: QObject | None, interval_ms: int, *slots: Callable[[], Any]) -> Timer:
    """
    Instantiate a new timer. **slots** are called immediately.

    :param parent: The QObject that owns this timer.
    :param interval_ms: The timeout in milliseconds.
    :param slots: The function(s) to connect the timer's timeout signal to.

    :returns: The created timer. The timer is already started. Note that you must keep a reference
    to the timer so it does not get deleted.
    """
    timer = Timer(parent, interval_ms, *slots)
    timer.start_fast()
    return timer
