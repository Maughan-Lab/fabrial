from ..base.item_info import BaseItemInfo
from .widget import TestWidget
from .process import TestProcess


class TestItemInfo(BaseItemInfo):
    WIDGET_TYPE = TestWidget
    PROCESS_TYPE = TestProcess
