from enum import Enum
from typing import Self
from .base import BaseWidget
from .null import NullWidget
from .test import TestWidget


class WidgetType(Enum):
    NULL = 0
    TEST = 1

    def to_class(self) -> type[BaseWidget | NullWidget]:
        """Return a widget class."""
        match self:
            case WidgetType.NULL:
                return NullWidget
            case WidgetType.TEST:
                return TestWidget
        print("Error, we should have already returned.")

    @classmethod
    # signature is weird because mypy hates me
    def from_class_object(cls: type[Self], class_object: object) -> "WidgetType":
        match class_object:
            case NullWidget():
                return WidgetType.NULL
            case TestWidget():  # this does not create a new instance, so no wasted time!
                return WidgetType.TEST
        print("should have already returned, ERROR")
        return WidgetType.NULL
