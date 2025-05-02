import os

from jinja2 import TemplateNotFound

from .. import Files
from ..classes.descriptions import DescriptionInfo
from .jinja import parse_template


def get_description(description_info: DescriptionInfo) -> str:
    """
    Get a Markdown description string from **description_info**. If any of the folders inside
    **description_info** do not exist, the application's default descriptions are used. If any
    description files do not exist, the application's default description is used for that category.
    """
    substitutions = description_info.substitutions
    Descriptions = Files.SequenceBuilder.Descriptions
    folder = os.path.join(
        Descriptions.FOLDER, description_info.category_folder, description_info.item_folder
    )

    # initially contains keys for the data recording section
    category_substitutions = {
        Descriptions.DataRecording.DIRECTORY_KEY: description_info.data_folder,
        Descriptions.DataRecording.METADATA_KEY: Files.Process.Filenames.METADATA,
    }
    # put the substituted text for each category into a substitution dictionary for the template
    # file
    for category, substitution_dict in (
        (Descriptions.Overview, substitutions.overview_dict),
        (Descriptions.Parameters, substitutions.parameters_dict),
        (Descriptions.Visuals, substitutions.visuals_dict),
        (Descriptions.DataRecording, substitutions.data_recording_dict),
    ):
        # if parsing the template fails (usually because the file doesn't exist), use the default
        # file instead
        try:
            category_substitution = parse_template(folder, category.FILENAME, substitution_dict)
        except TemplateNotFound:
            category_substitution = parse_template(
                os.path.join(Descriptions.FOLDER, Descriptions.DEFAULT_FOLDER),
                category.FILENAME,
            )
        category_substitutions[category.KEY] = category_substitution

    description = parse_template(
        Descriptions.FOLDER, Descriptions.TEMPLATE_FILENAME, category_substitutions
    )
    return description
