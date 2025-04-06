from dataclasses import dataclass
from .widget import BaseWidget
from ..root.widget import NullWidget
from .process import BaseProcess


@dataclass
class BaseItemInfo:
    """
    Base dataclass containing initialization information for the item. You must override:
    - `WIDGET_TYPE`
    - `PROCESS_TYPE`
    When using this class, you should not create an object. You should use this as a static storage
    container.
    """

    WIDGET_TYPE: type[BaseWidget | NullWidget] = BaseWidget
    PROCESS_TYPE: type[BaseProcess] = BaseProcess
    SUPPORTS_SUBITEMS: bool = False
