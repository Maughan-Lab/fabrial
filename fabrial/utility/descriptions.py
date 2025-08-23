import logging
import tomllib
from abc import abstractmethod
from dataclasses import dataclass, field
from os import PathLike
from typing import Protocol

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound, UndefinedError

from ..constants.paths.descriptions import (
    DATA_RECORDING_FILENAME,
    OVERVIEW_FILENAME,
    PARAMETERS_FILENAME,
    VISUALS_FILENAME,
)
from ..constants.sequence import METADATA_FILENAME

NO_DESCRIPTION_PROVIDED = "No description provided."
ERROR_TEXT = "Error loading description."

TEMPLATE = """{OVERVIEW}
# Parameters
{PARAMETERS}
# Visuals
{VISUALS}
# Data Recording
{DATA_RECORDING}"""

DATA_RECORDING_TEMPLATE = f"""Data is written to **{{DATA_DIRECTORY_NAME}}**, which contains:
- **{METADATA_FILENAME}**

    Metadata for this sequence step.
{{DATA_RECORDING_TEXT}}"""


class DescriptionProvider(Protocol):
    """An object that can provide a Markdown description string through its `render()` method."""

    @abstractmethod
    def render(self) -> str:
        """Generate the description."""
        ...


@dataclass
class TextDescription(DescriptionProvider):
    """
    Renders a description using text.

    Parameters
    ----------
    data_directory_name
        The name of the directory where the item records data.
    overview
        Text for the **Overview** section.
    parameters
        A mapping of `{"Parameter Name": "Description of parameter."}`. This will be rendered to a
        Markdown list for the **Parameters** section. Can be `{}` for no parameters.
    data_recording
        A mapping of `{"Filename": "Description of file contents."}`. This will be rendered to a
        Markdown list for the **Data Recording** section. Optional if your sequence step doesn't
        record extra data.
    visuals
        Text for the **Visuals** section. Optional if your sequence step doesn't have visuals.
    """

    data_directory_name: str
    overview: str
    parameters: dict[str, str]
    data_recording: dict[str, str] = field(default_factory=dict)
    visuals: str = "n/a"

    def render(self) -> str:  # implementation
        parameters_text = (
            generate_list_description(self.parameters) if len(self.parameters) > 0 else "n/a"
        )
        data_recording_text = (
            generate_list_description(self.data_recording) if len(self.data_recording) > 0 else ""
        )
        return TEMPLATE.format(
            OVERVIEW=self.overview,
            PARAMETERS=parameters_text,
            VISUALS=self.visuals,
            DATA_RECORDING=DATA_RECORDING_TEMPLATE.format(
                DATA_DIRECTORY_NAME=self.data_directory_name,
                DATA_RECORDING_TEXT=data_recording_text,
            ),
        )


@dataclass
class Substitutions:
    """
    Text-substitution dictionaries used by `jinja2`.

    Parameters
    ----------
    overview
        Substitutions for the **Overview** section.
    parameters
        Substitutions for the **Parameters** section.
    visuals
        Substitutions for the **Visuals** section.
    data_recording
        Substitutions for the **Data Recording** section.
    """

    overview: dict[str, str] = field(default_factory=dict)
    parameters: dict[str, str] = field(default_factory=dict)
    visuals: dict[str, str] = field(default_factory=dict)
    data_recording: dict[str, str] = field(default_factory=dict)


@dataclass
class FilesDescription(DescriptionProvider):
    """
    Renders a description by reading files in a folder.

    Parameters
    ----------
    description_folder
        The folder to read description files from. The folder should have the following structure:
    ```
    description_folder
    ├── data_recording.toml
    ├── overview.md
    ├── parameters.toml
    └── visuals.md
    ```
     For an example, see the [example directory](TODO). All files are mandatory, but only the
     overview file needs to have text (defaults will be used for the others).

    data_directory_name
        The name (i.e. not full path) of the directory that the item's process writes data to.
    substitutions
        Substitutions dictionaries used by `jinja2` when rendering the description files.
    """

    description_folder: PathLike[str] | str
    data_directory_name: str
    substitutions: Substitutions = field(default_factory=Substitutions)

    def render(self) -> str:  # implementation
        environment = Environment(
            loader=FileSystemLoader(self.description_folder), undefined=StrictUndefined
        )
        final_substitutions: dict[str, str] = {}

        # helper function to render a Markdown file
        def render_markdown(
            filename: str, substitution_dict: dict[str, str], empty_default: str
        ) -> str:
            try:
                text = environment.get_template(filename).render(substitution_dict)
                if text == "":
                    return empty_default
                return text
            except TemplateNotFound:
                return NO_DESCRIPTION_PROVIDED
            except UndefinedError:
                logging.getLogger(__name__).exception("Undefined jinja2 substitution")
                return ERROR_TEXT

        # helper function to render a TOML file into Markdown
        def render_toml(
            filename: str,
            substitution_dict: dict[str, str],
            empty_default: str,
            markdown_format_string: str = "**",
        ) -> str:
            try:
                name_description_map: dict[str, str] = tomllib.loads(
                    environment.get_template(filename).render(substitution_dict)
                )
                if len(name_description_map) == 0:
                    return empty_default
                return generate_list_description(name_description_map, markdown_format_string)
            except Exception:
                logging.getLogger(__name__).exception("Failed to render TOML description file")
                raise

        # overview
        final_substitutions["OVERVIEW"] = render_markdown(
            OVERVIEW_FILENAME, self.substitutions.overview, NO_DESCRIPTION_PROVIDED
        )
        # visuals
        final_substitutions["VISUALS"] = render_markdown(
            VISUALS_FILENAME, self.substitutions.visuals, "n/a"
        )
        # parameters
        try:
            parameters_text = render_toml(PARAMETERS_FILENAME, self.substitutions.parameters, "n/a")
        except TemplateNotFound:
            parameters_text = NO_DESCRIPTION_PROVIDED
        except Exception:
            parameters_text = ERROR_TEXT
        final_substitutions["PARAMETERS"] = parameters_text
        # data recording
        try:
            data_recording_text = DATA_RECORDING_TEMPLATE.format(
                DATA_DIRECTORY_NAME=self.data_directory_name,
                DATA_RECORDING_TEXT=render_toml(
                    DATA_RECORDING_FILENAME, self.substitutions.data_recording, ""
                ),
            )
        except TemplateNotFound:
            data_recording_text = NO_DESCRIPTION_PROVIDED
        except Exception:
            data_recording_text = ERROR_TEXT
        final_substitutions["DATA_RECORDING"] = data_recording_text

        return TEMPLATE.format(**final_substitutions)


def generate_list_description(
    name_description_map: dict[str, str], markdown_format_string: str = "**"
) -> str:
    """
    Creates a Markdown list string.

    Parameters
    ----------
    name_description_map
        A mapping of parameter names to their description.
    markdown_format_string
        The format string to place on both sides of the parameter name. For example, `**` will make
        the parameter name bold.

    Examples
    --------
    >>> generate_list_description(
    ...     {
    ...         "Parameter1": "Description of Parameter1.",
    ...         "Parameter2": "Description of Parameter2."
    ...     },
    ...     "**",
    ... )
    When rendered with Markdown, this yields:

    - **Parameter1**

        Description of Parameter1.
    - **Parameter2**

        Description of Parameter2.
    """
    return "\n".join(
        f"- {markdown_format_string}{name}{markdown_format_string}\n\n    {description}"
        for name, description in name_description_map.items()
    )
