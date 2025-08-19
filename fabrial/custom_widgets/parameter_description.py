from typing import Self

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QFrame, QLayout, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from .augmented import Widget
from .markdown_view import MarkdownView


class ParameterDescriptionWidget(Widget):
    """
    Widget with two tabs: one for parameters and one for description text.

    Parameters
    ----------
    parameter_layout
        The layout to use for the parameter tab.
    parameter_tab_name
        The text used for the parameter tab name.
    """

    def __init__(self, parameter_layout: QLayout | None, parameter_tab_name: str = "Parameters"):
        layout = QVBoxLayout()
        Widget.__init__(self, layout)
        self.param_widget = Widget(parameter_layout)
        parameter_scroll_area = QScrollArea()
        parameter_scroll_area.setWidget(self.param_widget)
        parameter_scroll_area.setWidgetResizable(True)
        parameter_scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.description_widget = MarkdownView()

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        tab_widget.addTab(parameter_scroll_area, parameter_tab_name)
        tab_widget.addTab(self.description_widget, "Description")

    def parameter_widget(self) -> QWidget:
        """Get the parameter widget (the first tab)."""
        return self.param_widget

    def set_description(self, text: str) -> Self:
        """Set the text (interpreted as Markdown) displayed in the description tab."""
        self.description_widget.setMarkdown(text)
        return self

    def sizeHint(self) -> QSize:
        return Widget.sizeHint(self) * 1.5
