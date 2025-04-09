from ...base.item_info import BaseItemInfo
from .widget import EISWidget
from .process import EISProcess


class EISItemInfo(BaseItemInfo):
    WIDGET_TYPE = EISWidget
    PROCESS_TYPE = EISProcess
