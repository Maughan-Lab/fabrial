from os import PathLike

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template


def make_template(folder: PathLike[str] | str, filename: str) -> Template:
    """
    Make a Jinja template from **folder** and **filename**.

    Raises
    ------
    jinja2.TemplateNotFound
        The file cannot be found.
    """
    environment = Environment(loader=FileSystemLoader(folder), undefined=StrictUndefined)
    return environment.get_template(filename)


def parse_template(
    folder: PathLike[str] | str, filename: str, template_dict: dict[str, str] = dict()
) -> str:
    """
    Parse a Jinja-templated file into a string.

    Parameters
    ----------
    folder
        The folder containing the template file.
    filename
        The name of the file *inside the folder* (i.e. not the full path).
    template_dict
        A dictionary to pass to Template.render().

    Raises
    ------
    jinja2.TemplateNotFound
        The file cannot be found.
    jinja2.UndefinedError
        There are undefined variables in the template.
    """
    return make_template(folder, filename).render(template_dict)
