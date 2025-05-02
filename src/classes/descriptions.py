from dataclasses import dataclass, field

from .. import Files


@dataclass
class DescriptionInfo:
    """
    Information for setting the description of an AbstractBaseWidget.

    :param category_folder: The name of the category folder inside the application's item
    description folder.
    :param item_folder: The name of the item folder inside the **category_folder**.
    :param data_folder: The name of the folder the associated process writes data to.
    :param substitutions: A collection of substitution dictionaries passed to the template renderer.
    """

    @dataclass
    class Substitutions:
        """Container for text-substitution dictionaries used by jinja."""

        overview_dict: dict[str, str] = field(default_factory=dict)
        """Substitutions for the overview section."""
        parameters_dict: dict[str, str] = field(default_factory=dict)
        """Substitutions for the parameters section."""
        visuals_dict: dict[str, str] = field(default_factory=dict)
        """Substitutions for the visuals section."""
        data_recording_dict: dict[str, str] = field(default_factory=dict)
        """Substitutions for the data recording section."""

    category_folder: str = Files.SequenceBuilder.Descriptions.DEFAULT_FOLDER
    item_folder: str = ""
    data_folder: str = ""
    substitutions: Substitutions = field(default_factory=Substitutions)
