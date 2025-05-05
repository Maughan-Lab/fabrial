import os

from jinja2 import TemplateNotFound

from ..classes.descriptions import DescriptionInfo
from ..Files.Process.Filenames import METADATA as METADATA_FILENAME
from ..Files.SequenceBuilder.Descriptions import (
    DEFAULT_FOLDER_NAME,
    FOLDER,
    TEMPLATE_FILENAME,
    DataRecording,
    Overview,
    Parameters,
    Visuals,
)
from .jinja import parse_template


def get_description(description_info: DescriptionInfo) -> str:
    """
    Get a Markdown description string from **description_info**. If any of the folders inside
    **description_info** do not exist, the application's default descriptions are used. If any
    description files do not exist, the application's default description is used for that category.
    """
    substitutions = description_info.substitutions
    folder = os.path.join(FOLDER, description_info.category_folder, description_info.item_folder)

    # initially contains keys for the data recording section
    category_substitutions = {
        DataRecording.DIRECTORY_KEY: description_info.data_folder,
        DataRecording.METADATA_KEY: METADATA_FILENAME,
    }
    # put the substituted text for each category into a substitution dictionary for the template
    # file
    for filename, key, substitution_dict in (
        (Overview.FILENAME, Overview.KEY, substitutions.overview_dict),
        (Parameters.FILENAME, Parameters.KEY, substitutions.parameters_dict),
        (Visuals.FILENAME, Visuals.KEY, substitutions.visuals_dict),
        (DataRecording.FILENAME, DataRecording.KEY, substitutions.data_recording_dict),
    ):
        # if parsing the template fails (usually because the file doesn't exist), use the default
        # file instead
        try:
            category_substitution = parse_template(folder, filename, substitution_dict)
        except TemplateNotFound:
            category_substitution = parse_template(
                os.path.join(FOLDER, DEFAULT_FOLDER_NAME), filename
            )
        category_substitutions[key] = category_substitution

    description = parse_template(FOLDER, TEMPLATE_FILENAME, category_substitutions)
    return description
