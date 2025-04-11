from PyQt6.QtWidgets import QWidget, QBoxLayout, QStackedLayout, QFormLayout, QLayout, QLayoutItem
from typing import Callable, TypeVar

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


# def add_sublayout_to_grid(
#     outer_layout: QGridLayout,
#     layout_fn: Callable[[], Layout],
#     row: int,
#     column: int,
#     size_policy: QSizePolicy.Policy = QSizePolicy.Policy.Preferred,
# ) -> Layout:
#     """
#     Add an inner layout to an outer grid layout.

#     :param outer_layout: The grid layout to add an inner layout to.
#     :param layout_fn: A callable constructor for the inner layout (i.e. **QGridLayout**, not
#     **QGridLayout()**)
#     :param row: The row to add the sublayout to.
#     :param column: The column to add the sublayout to.
#     :param size_policy: Optional policy for how the widgets inside the layout should expand. Use
#     **QSizePolicy.Fixed** to make sure labels do not expand.

#     :returns: The inner layout added to **layout**. This layout will have a matching type to
#     **type_of_layout_to_add**.

#     :raises: Throws an exception if **type_of_layout_to_add** is not callable.
#     """
#     try:
#         inner_layout = layout_fn()
#         inner_layout.setContentsMargins(0, 0, 0, 0)  # type: ignore
#         container = QWidget()
#         container.setLayout(inner_layout)  # type: ignore
#         container.setSizePolicy(size_policy, size_policy)
#         outer_layout.addWidget(container, row, column)
#         return inner_layout
#     except Exception as e:
#         print("`type_of_layout_to_add` must be a callable constructor for a `QLayout`.")
#         raise e


def add_to_layout(layout: QBoxLayout | QStackedLayout, *widgets: QWidget):
    """
    Adds widgets to a QBoxLayout or QStackedLayout. Cannot handle alignment or stretch.

    :param layout: The layout to add the widgets to.
    :param widgets: The widgets to add.
    """
    for widget in widgets:
        layout.addWidget(widget)


# def add_to_layout_grid(layout: QGridLayout, *widgets_rows_columns: tuple[QWidget, int, int]):
#     """
#     Adds widgets to a QGridLayout. Cannot handle alignment.

#     :param layout: The layout to add the widgets to.
#     :param widgets_rows_columns: Tuples containing the widget, the row, and the column—i.e.
#     `(QWidget(), 0, 2)` for a **QWidget** in row 0 and column 2.
#     """
#     for widget, row, column in widgets_rows_columns:
#         layout.addWidget(widget, row, column)


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


# def row_pair(
#     widget1: QWidget, widget2: QWidget, row: int
# ) -> tuple[tuple[QWidget, int, int], tuple[QWidget, int, int]]:
#     """
#     Generate a tuple in the form of ((widget1, row, COLUMN1), (widget2, row, COLUMN2)), where
#     COLUMN1 is 0 and COLUMN2 is 1. This can be unpacked for use with **add_to_layout_grid()**.
#     """
#     return ((widget1, row, 0), (widget2, row, 1))


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
