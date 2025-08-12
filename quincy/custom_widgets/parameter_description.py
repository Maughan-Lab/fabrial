from typing import Self

from PyQt6.QtWidgets import QFrame, QScrollArea, QTabWidget, QVBoxLayout, QWidget

from .augmented import Widget
from .markdown_view import MarkdownView


class ParameterDescriptionWidget(Widget):
    """
    Widget with two tabs: one for parameters and one for description text.

    Parameters
    ----------
    parameter_widget
        The widget to use for the parameter tab.
    parameter_tab_name
        The text used for the parameter tab name.
    """

    def __init__(self, parameter_widget: QWidget, parameter_tab_name: str = "Parameters"):
        layout = QVBoxLayout()
        Widget.__init__(self, layout)
        self.parameter_widget = parameter_widget
        self.parameter_widget.setContentsMargins(10, 10, 10, 10)  # looks better
        parameter_scroll_area = QScrollArea()
        parameter_scroll_area.setWidget(self.parameter_widget)
        parameter_scroll_area.setWidgetResizable(True)
        parameter_scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.description_widget = MarkdownView()

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        tab_widget.addTab(parameter_scroll_area, parameter_tab_name)
        tab_widget.addTab(self.description_widget, "Description")

    def get_parameter_widget(self) -> QWidget:
        """Get the parameter widget (the first tab)."""
        return self.parameter_widget

    def set_description(self, text: str) -> Self:
        """Set the text (interpreted as Markdown) displayed in the description tab."""
        self.description_widget.setMarkdown(text)
        return self


# class ParameterDescriptionWidget(Widget):
#     """
#     Widget with two tabs: one for parameters and one for description text.

#     Parameters
#     ----------
#     layout
#         The layout for the parameter tab widget.
#     parameter_tab_name
#         The text used for the parameter tab name.
#     """

#     def __init__(self, parameter_layout: QLayout, parameter_tab_name: str = "Parameters"):
#         layout = QVBoxLayout()
#         Widget.__init__(self, layout)
#         self.tab_widget = QTabWidget(self)
#         layout.addWidget(self.tab_widget)

#         self.parameter_tab: QWidget = Widget(parameter_layout)
#         self.tab_widget.addTab(self.parameter_tab, parameter_tab_name)

#         description_layout = QVBoxLayout()
#         self.description_tab = Widget(description_layout)
#         self.description_widget = MarkdownView()
#         description_layout.addWidget(
#             self.description_widget, alignment=Qt.AlignmentFlag.AlignHCenter
#         )

#         self.tab_widget.addTab(self.description_tab, "Description")

#     # TODO: rename this method to `get_parameter_widget()`
#     def parameter_widget(self) -> QWidget:
#         """Get the parameter tab widget."""
#         return self.parameter_tab

#     # TODO: remove this method
#     def set_parameter_widget(self, widget: QWidget) -> Self:
#         """Set the parameter tab widget."""
#         layout: QVBoxLayout = self.layout()  # type: ignore
#         layout.replaceWidget(self.parameter_tab, widget)
#         self.parameter_tab = widget
#         return self

#     def set_description(self, text: str) -> Self:
#         """Set the text (interpreted as Markdown) displayed in the description tab."""
#         self.description_widget.setMarkdown(text)
#         return self

#     # TODO: remove this method
#     def set_description_from_file(
#         self, folder: PathLike[str] | str, filename: str, template_dict: dict[str, str] = dict()
#     ) -> Self:
#         """
#         Set the text (interpreted as Markdown) displayed in the description tab by parsing a
#         Jinja-templated file.

#         Parameters
#         ----------
#         folder
#             The folder that contains the text file.
#         filename
#             The name of the file *inside the folder* (i.e. not the full path).
#         template_dict
#             A dictionary to pass to jinja2.Template.render().
#         """
#         markdown_text = jinja.parse_template(folder, filename, template_dict)
#         return self.set_description(markdown_text)
