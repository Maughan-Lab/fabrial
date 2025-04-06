from ..base.item_info import BaseItemInfo
from .widget import LoopWidget
from .process import LoopProcess


class LoopItemInfo(BaseItemInfo):
    WIDGET_TYPE = LoopWidget
    PROCESS_TYPE = LoopProcess
    SUPPORTS_SUBITEMS = True
