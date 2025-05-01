from jinja2 import Environment, FileSystemLoader, StrictUndefined


def make_template(folder: str, filename: str):
    """
    Make a Jinja template from **folder** and **filename**.

    :raises: **jinja2.TemplateNotFound** if the file cannot be found.
    """
    environment = Environment(loader=FileSystemLoader(folder), undefined=StrictUndefined)
    return environment.get_template(filename)


def parse_template(folder: str, filename: str, template_dict: dict[str, str] = dict()) -> str:
    """
    Parse a Jinja-templated file into a string.

    :param folder: The folder containing the template file.
    :param filename: The name of the file *inside the folder* (i.e. not the full path).
    :param template_dict: A dictionary to pass to Template.render().

    :raises: **jinja2.TemplateNotFound** if the file cannot be found.
    :raises: **jinja2.UndefinedError** if there are undefined variables in the template.
    """
    return make_template(folder, filename).render(template_dict)
