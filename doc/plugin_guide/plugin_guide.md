## Creating a Plugin for Fabrial

In this tutorial, we're going to write a Fabrial plugin called `random_data`. It will add one action to the sequence builder which records random data on a user-specified interval. Our plugin will also have its own tab in the settings menu. If you get stuck and need an example, check out the [core plugins](https://github.com/Maughan-Lab/fabrial-core-plugins). The completed files for this tutorial can also be found [here](./my_plugin/).

This guide is geared towards inexperienced programmers. If you've written a lot of Python, you can likely skip some sections.

### What Makes a Plugin?

A plugin is just a bunch of Python code that adheres to some requirements. Fabrial plugins have pre-defined *entry points*, which are functions Fabrial calls to access the plugin's code. Fabrial has a few entry point functions; we'll talk about them later on.

### Local or Global?

You can write either a *local plugin* or a *global plugin*. Local plugins go in the [**`plugins`**](../../fabrial/plugins/) folder and can be installed/uninstalled from the settings. In contrast, global plugins are installed into your Python environment just like any other Python package.

Global plugins require slightly more setup, but they also double as local plugins. Local plugins are more restricted, but they are simpler to write and can be converted to global plugins later.

We'll start by creating a local plugin, then we'll convert it to a global plugin.

## Getting Started

> Ensure your Python version is at least `3.13`. You can check with `python --version`.

> This tutorial uses [type annotations](https://docs.python.org/3/library/typing.html). I highly recommended you set up [`mypy`](https://mypy.readthedocs.io/en/stable/getting_started.html) or some other type checker. Type checkers can catch common errors before you even run your plugin, and they encourage readable and maintainable code. If you are using [VS Code](https://code.visualstudio.com/), there are two `mypy` extensions available: [Mypy](https://marketplace.visualstudio.com/items?itemName=matangover.mypy) and [Mypy Type Checker](https://marketplace.visualstudio.com/items?itemName=ms-python.mypy-type-checker).

To start, we need to set up a development environment (i.e. a place to write our plugin code). Choose a folder to put everything in, for example **`my_plugin`**. Then, [create and activate a virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments). We may need to install a few Python packages—virtual environments let us do so without cluttering up our global Python installation. Install Fabrial and its dependencies with
```
pip install fabrial
```
Let's create our plugin module. Make a folder called **`random_data`** and put an empty **`__init__.py`** file inside. At this point, the project folder should look like this:

```
my_plugin
├── .venv
│   └── --snip--
└── random_data
    └── __init__.py
```

> #### Testing as You Go
>
> If you want to test your plugin as you write it, you'll need to "install" it. The simplest way is to place the plugin folder (**`random_data`** for this tutorial) in Fabrial's **`plugins`** folder (i.e. move it out of **`my_plugin`**). In your virtual environment, you can find this in **`site_packages/fabrial/plugins`**.
>
>> Alternatively, you can install Fabrial in a virtual environment and install your plugin in [editable mode](https://setuptools.pypa.io/en/latest/userguide/development_mode.html). This requires a **`pyproject.toml`** file, see [Converting to a Global Plugin](#converting-to-a-global-plugin).
>
>If you run
>
> ```
> fabrial
> ```
>
> from the command line, you should see an error message when the application loads. Good! That means your plugin is being detected by Fabrial.

## Creating an Item for the Sequence Builder
> **Advanced users:** If you *really* don't want to use a widget, you can use the [`DataItem`](../../fabrial/sequence_builder/data_item.py) protocol instead of the `WidgetDataItem` protocol for your item. This is not recommended and is not covered in this tutorial.

Actions in the sequence builder have three components:
1. The widget containing an icon, parameters, and a description,
2. The drag-and-droppable item,
3. The step that gets run by the sequence.

Let's create their files. Inside **`random_data`**, create **`random_widget.py`**, **`random_item.py`**, and **`random_step.py`**. We'll also need an icon for our widget. We can use the [example icon](./my_plugin/random_data/example_icon.png) which depicts sushi. Delicious!

The file structure should look like this:
```
random_data
├── example_icon.png
├── __init__.py
├── random_item.py
├── random_step.py
└── random_widget.py
```

We need to implement the widget, the item, and the sequence step. The guides below should be followed in order. When you have completed all three, return here.

- [Implementing the Widget](./widget.md)

- [Implementing the Item](./item.md)

- [Implementing the Sequence Step](./step.md)

Now that we've implemented all the components, let's address an earlier laziness. Our item's `create_sequence_step()` method currently raises an exception. It should return an instance of our sequence step instead.

<sub>Filename: random_data/random_item.py</sub>
```python
# --snip--

from .random_step import RandomDataStep

# --snip--

    def create_sequence_step(self, substeps: Iterable[SequenceStep]) -> SequenceStep:
        return RandomDataStep(self.random_data_widget.interval_spinbox.value())
```

Technically, our sequence action is now finished. If you copy **`random_data`** to Fabrial's **`plugins`** folder, our item will show up, and using it in a sequence will record random data. However, there are a number of ways to make it better.

Follow the [expanding our sequence step](./advanced_step.md) guide, then we'll get into the last part of the tutorial—adding a tab to the settings menu.

## Plugin Settings

TODO; ignore this for now

## Converting to a Global Plugin

> This section is optional if you only want a local plugin.

To convert a local plugin to a global plugin, we just need to make it buildable. We'll use [`hatch`](https://hatch.pypa.io/latest/) to build our plugin.

Move your plugin module back into **`my_plugin`**, then create a **`README.md`** file and a **`pyproject.toml`** file. We'll set up a basic **`pyproject.toml`**, but additional information about this file can be found [here](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/). The project folder should look like this:

```
my_plugin
├── pyproject.toml
├── random_data
│   ├── descriptions
│   │   └── --snip--
│   ├── example_icon.png
│   ├── __init__.py
│   ├── random_item.py
│   ├── random_step.py
│   └── random_widget.py
└── README.md
```

Put a brief description of the plugin in **`README.md`**. Then, put the following in **`pyproject.toml`**.

<sub>Filename: my_plugin/pyproject.toml</sub>
```
[project]
name = "random_data"
version = "0.1.0"

dependencies = ["fabrial", "PyQt6"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.entry-points."fabrial.plugins"]
random-data = "random_data"
```

The `[project]` table and its `name` and `version` keys are required. For basic use, the value of `name` must be the same as folder where the Python code is stored. The value of `dependencies` is a list of Python packages the project requires (`PyQt6` and `fabrial` for this plugin).

The `[build-system]` table defines how to build our project using `Hatch`.

The last table is required for Fabrial to recognize the plugin when it's installed. `"fabrial.plugins"` is Fabrial's module-level entry point. The keys should be plugin names (i.e. `random-data`) and the values should be module names (i.e. `random_data`).

Inside **`my_plugin`**, run

```
pip install .
```

to build the plugin and install it into your Python environment. If Fabrial and our plugin are installed in the same Python environment, Fabrial will load our plugin automatically. Huzzah!

___

Congratulations! You've written a fully-functional plugin for Fabrial. Although the plugin we wrote during this tutorial is not very useful, you've learned the principles behind all Fabrial plugins. If you have any questions or ideas for improving this tutorial, feel free to start a [discussion on GitHub](https://github.com/Maughan-Lab/fabrial/discussions).

If you want to make your plugin available for other people, consider publishing on [PyPi](https://pypi.org/). The publication process is outside the scope of this tutorial, but a great guide can be found [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/).