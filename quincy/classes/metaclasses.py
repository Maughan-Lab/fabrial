from typing import Protocol

from PyQt6.QtCore import QObject


class QProtocolMeta(Protocol, type(QObject)):  # type: ignore
    """Metaclass combining `Protocol` and `QObject`."""
