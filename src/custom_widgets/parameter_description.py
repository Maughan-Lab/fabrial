from typing import Self

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLayout, QTabWidget, QVBoxLayout, QWidget

from ..utility.jinja import parse_template
from .augmented.widget import Widget
from .markdown_view import MarkdownView


class ParameterDescriptionWidget(Widget):
    """Widget with two tabs: one for parameters and one for description text."""

    def __init__(
        self, parameter_layout: QLayout | None = None, parameter_tab_name: str = "Parameters"
    ):
        """
        :param layout: The layout for the parameter tab widget.
        :param parameter_tab_name: The text used for the parameter tab name.
        """

        layout = QVBoxLayout()
        super().__init__(layout)
        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        self.parameter_tab: QWidget = Widget(parameter_layout)
        self.tab_widget.addTab(self.parameter_tab, parameter_tab_name)

        description_layout = QVBoxLayout()
        self.description_tab = Widget(description_layout)
        self.description_widget = MarkdownView()
        description_layout.addWidget(
            self.description_widget, alignment=Qt.AlignmentFlag.AlignHCenter
        )

        self.tab_widget.addTab(self.description_tab, "Description")

    def parameter_widget(self) -> QWidget:
        """Get the parameter tab widget."""
        return self.parameter_tab

    def set_parameter_widget(self, widget: QWidget) -> Self:
        """Set the parameter tab widget."""
        layout: QVBoxLayout = self.layout()  # type: ignore
        layout.replaceWidget(self.parameter_tab, widget)
        self.parameter_tab = widget
        return self

    def set_description(self, text: str) -> Self:
        """Set the text (interpreted as Markdown) displayed in the description tab."""
        self.description_widget.setMarkdown(text)
        return self

    def set_description_from_file(
        self, folder: str, filename: str, template_dict: dict[str, str] = dict()
    ) -> Self:
        """
        Set the text (interpreted as Markdown) displayed in the description tab by parsing a
        Jinja-templated file.

        :param folder: The folder that contains the text file.
        :param filename: The name of the file *inside the folder* (i.e. not the full path).
        :param template_dict: A dictionary to pass to jinja2.Template.render().
        """
        markdown_text = parse_template(folder, filename, template_dict)
        return self.set_description(markdown_text)
