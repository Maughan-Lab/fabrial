from abc import ABCMeta
from typing import Protocol

from PyQt6.QtCore import QObject


class QProtocolMeta(type(QObject), type(Protocol)):  # type: ignore
    """Metaclass combining `Protocol` and `QObject`."""


class QProtocol(Protocol, metaclass=QProtocolMeta):
    pass


class ABCQObjectMeta(ABCMeta, type(QObject)):  # type: ignore
    pass


class QABCMeta(ABCMeta, type(QObject)):  # type: ignore
    """Metaclass combing `ABCMeta` and QObject's metaclass."""


class QABC(metaclass=QABCMeta):
    """`ABC` with support for `QObject`s."""
