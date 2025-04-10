from jinja2 import Environment, FileSystemLoader


def parse_template(folder: str, filename: str, template_dict: dict[str, str]) -> str:
    """
    Parse a Jinja-templated file into a string.

    :param folder: The folder containing the template file.
    :param filename: The name of the file *inside the folder* (i.e. not the full path).
    :param template_dict: A dictionary to pass to Template.render().
    """

    environment = Environment(loader=FileSystemLoader(folder))
    template = environment.get_template(filename)
    return template.render(template_dict)
