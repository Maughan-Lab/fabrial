from ..base.item_info import CategoryInfo, CategoryWidget


class Widget(CategoryWidget):
    DISPLAY_NAME = "EIS"


class EISCategoryInfo(CategoryInfo):
    WIDGET_TYPE = Widget
