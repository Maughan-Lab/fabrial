## Creating a Plugin for Fabrial
In this tutorial, we're going to write a Fabrial plugin called `random_data`. It will add one item to the sequence builder and have its own tab in the settings menu.

### What Makes a Plugin?
A plugin is just a bunch of Python code that adheres to some requirements. Fabrial plugins have pre-defined *entry points*, which are functions Fabrial calls to access the plugin's code. Fabrial has a few entry point functions; we'll talk about them later on.

### Local or Global?
When creating a Fabrial plugin, you can write either a *local plugin* or a *global plugin*. Local plugins go in the `plugins` directory and can be installed/uninstalled from the settings. In contrast, global plugins are installed into your Python environment just like any other Python package.

Global plugins require slightly more setup, but they also double as local plugins. Local plugins are more restricted, but they are simpler to write and can be converted to global plugins later.

We'll start by creating a local plugin, then we'll convert it to a global plugin.

## Getting Started
 >Ensure your Python version is at least `3.13`. You can check with `python --version`.

To start, we need to set up a development environment (i.e. a place to write our plugin code). Choose a folder to put everything in, for example `my_plugin`. Then, [create and activate a virtual environment](https://docs.python.org/3/tutorial/venv.html#creating-virtual-environments). We may need to install a few Python packages—virtual environments let us do so without cluttering up our global Python installation. Install Fabrial with
```
pip install fabrial
```
Let's create our plugin module. Make a folder called `random_data` and put an empty `__init__.py` inside. At this point, the project folder should look like below
```
my_plugin
├── .venv
│   └── ...
└── random_data
    └── __init__.py
```

### Creating an Item in the Sequence Builder
TODO