import os

from jinja2 import TemplateNotFound

from ..classes.descriptions import DescriptionInfo
from ..constants.paths.process.filenames import METADATA as METADATA_FILENAME
from ..constants.paths.sequence_builder.descriptions import (
    DEFAULT_FOLDER_NAME,
    FOLDER,
    TEMPLATE_FILENAME,
    data_recording,
    overview,
    parameters,
    visuals,
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
        data_recording.DIRECTORY_KEY: description_info.data_folder,
        data_recording.METADATA_KEY: METADATA_FILENAME,
    }
    # put the substituted text for each category into a substitution dictionary for the template
    # file
    for filename, key, substitution_dict in (
        (overview.FILENAME, overview.KEY, substitutions.overview_dict),
        (parameters.FILENAME, parameters.KEY, substitutions.parameters_dict),
        (visuals.FILENAME, visuals.KEY, substitutions.visuals_dict),
        (data_recording.FILENAME, data_recording.KEY, substitutions.data_recording_dict),
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
