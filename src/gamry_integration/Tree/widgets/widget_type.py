from enum import Enum
from typing import Self


class WidgetType(Enum):
    POTENTIOSTATIC_EIS = 0
    TEST = 1

    def to_class(self) -> type:
        """Return a widget class."""
        # match self:
        #     case WidgetType.POTENTIOSTATIC_EIS:
        #         return TestWidget
        #     case WidgetType.TEST:
        #         return TestWidget
        return type

    @classmethod
    def from_class_object(cls: type[Self], class_object: object) -> "WidgetType":
        # match class_object:
        #     case TestWidget():  # this does not create a new instance, so no wasted time!
        #         return WidgetType.TEST
        # print("should have already returned, ERROR")
        return WidgetType.TEST
