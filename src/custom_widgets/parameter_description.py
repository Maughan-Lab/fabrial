from .widget import Widget
from .widget import FixedWidget
from .markdown_label import MarkdownLabel
from typing import Self
from PyQt6.QtWidgets import QVBoxLayout, QLayout, QTabWidget, QWidget
from .. import Files
from ..utility.jinja import parse_template
import os


class ParameterDescriptionWidget(Widget):
    """Widget with two tabs: one for parameters and one for description text."""

    def __init__(self, parameter_layout: QLayout):
        """:param layout: The layout for the parameter tab widget."""

        layout = QVBoxLayout()
        super().__init__(layout)
        self.tab_widget = QTabWidget(self)
        layout.addWidget(self.tab_widget)

        self.parameter_tab: QWidget = FixedWidget()
        self.parameter_tab.setLayout(parameter_layout)

        self.tab_widget.addTab(self.parameter_tab, "Parameters")

        self.description_tab = MarkdownLabel()
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
        self.description_tab.setMarkdown(text)
        return self

    def set_description_from_file(
        self, category_folder: str, filename: str, template_dict: dict[str, str]
    ) -> Self:
        """
        Set the text (interpreted as Markdown) displayed in the description tab by parsing a
        Jinja-templated file.

        :param category_folder: The name of the category folder containing the template file.
        :param filename: The name of the file *inside the folder* (i.e. not the full path).
        :param template_dict: A dictionary to pass to Template.render().
        """
        folder = os.path.join(Files.SequenceBuilder.DESCRIPTIONS, category_folder)
        markdown_text = parse_template(folder, filename, template_dict)
        self.description_tab.setMarkdown(markdown_text)
        return self
