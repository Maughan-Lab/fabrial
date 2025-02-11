from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates"))

templete = env.get_template("test.jinja")

output = templete.render(name="Dr. Maughan")

print(output)
