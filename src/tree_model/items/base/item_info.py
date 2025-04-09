from .widget import BaseWidget, CategoryWidget
from .process import BaseProcess


class BaseItemInfo:
    """
    Base dataclass containing initialization information for the item. You must override:
    - `WIDGET_TYPE`
    - `PROCESS_TYPE`
    When using this class, you should not create an object. You should use this as a static storage
    container.
    """

    WIDGET_TYPE: type[BaseWidget | CategoryWidget] = BaseWidget
    PROCESS_TYPE: type[BaseProcess] | None = None
    SUPPORTS_SUBITEMS: bool = False
    DRAGGABLE: bool = True


class CategoryInfo(BaseItemInfo):
    """Fake BaseItemInfo for category items."""

    WIDGET_TYPE: type[CategoryWidget] = CategoryWidget
    PROCESS_TYPE: None = None
    SUPPORTS_SUBITEMS = True
    DRAGGABLE = False
