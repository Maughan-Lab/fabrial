from typing import Any, Callable

from PyQt6.QtCore import QObject

from ..classes import Timer


def new_timer(parent: QObject | None, interval_ms: int, *slots: Callable[[], Any]) -> Timer:
    """
    Instantiate a new timer. The **slots** are called immediately.

    Parameters
    ----------
    parent
        The QObject that owns this timer.
    interval_ms
        The timeout in milliseconds.
    slots
        The function(s) to connect the timer's timeout signal to.

    Returns
    -------
    The created timer. The timer is already started. Note that you must keep a reference to the
    timer so it does not get deleted.
    """
    timer = Timer(parent, interval_ms, *slots)
    timer.start_fast()
    return timer
