from typing import Callable, TypeVar

from PyQt6.QtWidgets import QBoxLayout, QFormLayout, QLayout, QLayoutItem, QStackedLayout, QWidget

Layout = TypeVar("Layout", bound=QLayout)


def add_sublayout(outer_layout: QBoxLayout, layout_fn: Callable[[], Layout]) -> Layout:
    """
    Add an inner layout to an outer layout.

    :param outer_layout: The outer layout to add an inner layout to.
    :param layout_fn: A function to construct the inner layout (i.e. `QGridLayout`, not
    `QGridLayout()`)

    :returns: The inner layout added to **layout**.
    """
    inner_layout = layout_fn()
    outer_layout.addLayout(inner_layout)
    return inner_layout


def add_to_layout(layout: QBoxLayout | QStackedLayout, *widgets: QWidget):
    """
    Adds widgets to a QBoxLayout or QStackedLayout. Cannot handle alignment or stretch.

    :param layout: The layout to add the widgets to.
    :param widgets: The widgets to add.
    """
    for widget in widgets:
        layout.addWidget(widget)


def add_to_form_layout(layout: QFormLayout, *item_pair: tuple[QWidget | str, QWidget]):
    """
    Adds widgets to a QFormLayout.

    :param layout: The layout to add widgets to.
    :param item_pair: Item pair(s) in the form of (LEFT_ITEM, RIGHT_ITEM), where LEFT_ITEM is the
    item on the left and RIGHT_ITEM is the item on the right. If LEFT_ITEM is a `str`, a label will\
    be created with LEFT_ITEM as the text.
    """
    for pair in item_pair:
        layout.addRow(pair[0], pair[1])


def clear_layout(layout: QLayout):
    """Removes all widgets and sublayouts from the layout."""
    for i in reversed(range(layout.count())):
        # setting a widget's parent to None schedules it for deletion
        layout_item: QLayoutItem = layout.takeAt(i)  # type: ignore
        widget = layout_item.widget()
        if widget is not None:  # the item is a widget
            widget.setParent(None)
        else:  # the item is a layout
            contained_layout = layout_item.layout()
            if contained_layout is not None:
                contained_layout.setParent(None)
