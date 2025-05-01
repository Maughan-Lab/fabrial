from .. import Files
from ..classes.descriptions import DescriptionInfo
import os
from .jinja import parse_template
from jinja2 import TemplateNotFound


def get_description(description_info: DescriptionInfo) -> str:
    """Get a Markdown description string from **description_info**."""
    substitutions = description_info.substitutions
    Descriptions = Files.SequenceBuilder.Descriptions
    # if the category folder and item folder were not specified, the default folder is used
    folder = os.path.join(
        Descriptions.FOLDER, description_info.category_folder, description_info.item_folder
    )

    # put the substituted text for each category into a substitution dictionary for the template
    # file
    category_substitutions = {}
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
                {},
            )
        category_substitutions[category.KEY] = category_substitution

    description = parse_template(
        Descriptions.FOLDER, Descriptions.TEMPLATE_FILENAME, category_substitutions
    )
    return description
