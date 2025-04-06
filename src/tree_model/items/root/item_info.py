from ..base.item_info import BaseItemInfo
from .widget import NullWidget


class RootItemInfo(BaseItemInfo):
    WIDGET_TYPE = NullWidget
    # intentionally uses the default PROCESS_TYPE value
    SUPPORTS_SUBITEMS = True
