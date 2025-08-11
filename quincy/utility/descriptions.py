import tomllib
from dataclasses import dataclass, field
from os import PathLike

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound, UndefinedError

from ..constants.paths.process.filenames import METADATA_FILENAME
from ..constants.paths.sequence_builder.descriptions import (
    DATA_RECORDING_FILENAME,
    OVERVIEW_FILENAME,
    PARAMETERS_FILENAME,
    VISUALS_FILENAME,
)

NO_DESCRIPTION_PROVIDED = "No description provided."
ERROR_TEXT = "Error loading description."
TEMPLATE = """{OVERVIEW}
# Parameters
{PARAMETERS}
# Visuals
{VISUALS}
# Data Recording
{DATA_RECORDING}"""
DATA_RECORDING_TEMPLATE = f"""Data is written to `{{DATA_DIRECTORY_NAME}}`, which contains:
- `{METADATA_FILENAME}`

    Metadata for this sequence step.
{{DATA_RECORDING_TEXT}}"""


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
class DescriptionInfo:
    """
    Information used to set the description of an `ItemWidget`.

    Parameters
    ----------
    folder
        The folder to read description files from. The folder should have the following structure:
    ```
    folder
    ├── data_recording.toml
    ├── overview.md
    ├── parameters.toml
    └── visuals.md
    ```
     For an example, see the [example directory](TODO).

    data_directory_name
        The name (i.e. not full path) of the directory the item's process writes data to.
    substitutions
        Substitutions dictionaries used by `jinja2` when rendering the description files.
    """

    folder: PathLike[str] | str
    data_directory_name: str
    substitutions: Substitutions = field(default_factory=Substitutions)


def make_description(description_info: DescriptionInfo | None) -> str:
    """
    Create a Markdown description string based on **description_info**. If any description files do
    not exist, a default description is used.

    Returns
    -------
    The rendered Markdown string.
    """
    if description_info is None:
        return NO_DESCRIPTION_PROVIDED

    user_substitutions = description_info.substitutions
    environment = Environment(
        loader=FileSystemLoader(description_info.folder), undefined=StrictUndefined
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
        except UndefinedError as e:
            e
            # TODO: log error
            return ERROR_TEXT

    # helper function to render a TOML file into Markdown
    def render_toml(
        filename: str, substitution_dict: dict[str, str], format_string: str, empty_default: str
    ) -> str:
        try:
            parameter_text_groups: list[str] = []
            for name, description in tomllib.loads(
                environment.get_template(filename).render(substitution_dict)
            ).items():
                if not isinstance(description, str):
                    raise TypeError(
                        "TOML description files must contain key, value pairs "
                        "that are both strings"
                    )
                parameter_text_groups.append(
                    f"- {format_string}{name}{format_string}\n\n    {description}"
                )
            # makes something like
            # - `name`
            #
            #    description
            # - `name`
            #
            #    description
            # ...
            if len(parameter_text_groups) == 0:
                return empty_default
            return "\n".join(parameter_text_groups)
        except Exception as e:
            # TODO: log error
            e
            raise

    # overview
    final_substitutions["OVERVIEW"] = render_markdown(
        OVERVIEW_FILENAME, user_substitutions.overview, "n/a"
    )
    # visuals
    final_substitutions["VISUALS"] = render_markdown(
        VISUALS_FILENAME, user_substitutions.visuals, "n/a"
    )
    # parameters
    try:
        parameters_text = render_toml(
            PARAMETERS_FILENAME, user_substitutions.parameters, "**", "n/a"
        )
    except TemplateNotFound:
        parameters_text = NO_DESCRIPTION_PROVIDED
    except Exception:
        parameters_text = ERROR_TEXT
    final_substitutions["PARAMETERS"] = parameters_text
    # data recording
    try:
        data_recording_text = DATA_RECORDING_TEMPLATE.format(
            DATA_DIRECTORY_NAME=description_info.data_directory_name,
            DATA_RECORDING_TEXT=render_toml(
                DATA_RECORDING_FILENAME, user_substitutions.data_recording, "`", ""
            ),
        )
    except TemplateNotFound:
        data_recording_text = NO_DESCRIPTION_PROVIDED
    except Exception:
        data_recording_text = ERROR_TEXT
    final_substitutions["DATA_RECORDING"] = data_recording_text

    return TEMPLATE.format(**final_substitutions)
