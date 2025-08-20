from abc import ABCMeta

from PyQt6.QtCore import QObject


class QABCMeta(ABCMeta, type(QObject)):  # type: ignore
    """Metaclass combing `ABCMeta` and QObject's metaclass."""


class QABC(metaclass=QABCMeta):
    """`ABC` with support for `QObject`s."""
