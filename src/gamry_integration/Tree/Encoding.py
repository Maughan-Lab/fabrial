from dataclasses import dataclass


@dataclass
class TreeItem:
    TYPE = "linked-widget-type"
    DATA = "linked-widget-data"
    CHILDREN = "children"


@dataclass
class TestWidget:
    DISPLAY_NAME = "display-name"
    CRY_COUNT = "cry-count"
    AVERAGE_CRIES = "average-cries"
