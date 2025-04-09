from ..base.item_info import CategoryInfo, CategoryWidget


class Widget(CategoryWidget):
    DISPLAY_NAME = "Process Control"


class FlowControlCategoryInfo(CategoryInfo):
    WIDGET_TYPE = Widget
