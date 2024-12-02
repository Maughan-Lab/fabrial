from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QStackedLayout,
    QLayout,
    QSizePolicy,
)
from typing import Callable, TypeVar

Layout = TypeVar("Layout")


def add_sublayout(
    outer_layout: QLayout,
    layout_fn: Callable[[], Layout],
    size_policy: QSizePolicy.Policy = QSizePolicy.Policy.Preferred,
) -> Layout:
    """
    Function for adding inner layouts to outer layouts.

    :param outer_layout: The outer layout to add an inner layout to.

    :param layout_fn: A callable constructor for the inner layout (i.e. **QGridLayout**, not
    **QGridLayout()**)

    :param size_policy: Optional policy for how the widgets inside the layout should expand. Use
    **QSizePolicy.Fixed** to make sure labels do not expand.

    :returns: The inner layout added to **layout**. This layout will have a matching type to
    **type_of_layout_to_add**.

    :raises: Throws an exception if **type_of_layout_to_add** is not callable.
    """
    try:
        inner_layout = layout_fn()
        inner_layout.setContentsMargins(0, 0, 0, 0)
        container = QWidget()
        container.setLayout(inner_layout)
        container.setSizePolicy(size_policy, size_policy)
        outer_layout.addWidget(container)
        return inner_layout
    except Exception as e:
        print("`type_of_layout_to_add` must be a callable constructor for a `QLayout`.")
        raise e


def add_to_layout(layout: QHBoxLayout | QVBoxLayout | QStackedLayout, *widgets: QWidget):
    """
    Adds widgets to a QHBoxLayout or QVBoxLayout. Cannot handle alignment.

    :param layout: The layout to add the widgets to.

    :param widgets: The widgets to add.
    """
    for widget in widgets:
        layout.addWidget(widget)


def add_to_layout_grid(layout: QGridLayout, *widgets_rows_columns: tuple[QWidget, int, int]):
    """
    Adds widgets to a QGridLayout. Cannot handle alignment.

    :param layout: The layout to add the widgets to.

    :param widgets_rows_columns: Tuples containing the widget, the row, and the column—i.e.
    `(QWidget(), 0, 2)` for a **QWidget** in row 0 and column 2.
    """
    for widget, row, column in widgets_rows_columns:
        layout.addWidget(widget, row, column)
