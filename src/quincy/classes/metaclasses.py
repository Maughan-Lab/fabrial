from abc import ABCMeta

from PyQt6.QtCore import QObject


class ABCQObjectMeta(ABCMeta, type(QObject)):  # type: ignore
    """Metaclass combining **ABCMeta** and **QObject**."""
