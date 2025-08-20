## The Widget

Widgets inherit from [`ItemWidget`](../../fabrial/sequence_builder/item_widget.py). We need to import `ItemWidget` from Fabrial, plus some extra items as shown below.

<sub>Filename: random_data/random_widget.py</sub>
```python
from pathlib import Path

from fabrial import FilesDescription, ItemWidget, Substitutions, TextDescription
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QDoubleSpinBox, QFormLayout, QWidget
```

Next, let's create our widget class, `RandomDataWidget`.

<sub>Filename: random_data/random_widget.py</sub>
```python
# --snip--

# we'll refer to these constants a few times
NAME = "Random Data"
DIRECTORY = Path(__file__).parent
# you should create the icon once instead of inside `__init__()`
ICON = QIcon(str(DIRECTORY.joinpath("example_icon")))

# we inherit from `ItemWidget` so Fabrial can work with our custom widget
class RandomDataWidget(ItemWidget):
    """Record random data on an interval; widget."""

    pass
```

Our widget is pretty useless right now, so let's implement `__init__()`. Since we inherited from `ItemWidget`, we'll need to call its `__init__()` method.

<sub>Filename: random_data/random_widget.py</sub>
```python
# --snip--

class RandomDataWidget(ItemWidget):
    """Record random data on an interval; widget."""

    def __init__(self, data_interval: float):
        # this is a layout for other widgets
        layout = QFormLayout()
        # this widget holds the layout
        parameter_widget = QWidget()
        parameter_widget.setLayout(layout)

        # you must call the base `__init__()` method
        # for now, we're not supplying a description
        ItemWidget.__init__(self, parameter_widget, NAME, ICON, None)

        # let's create the widgets!
        self.interval_spinbox = QDoubleSpinBox()
        # minimum and maximum values
        self.interval_spinbox.setMinimum(0.1)
        self.interval_spinbox.setMaximum(1000)
        # start at the supplied value
        self.interval_spinbox.setValue(data_interval)
        # add the spinbox to the layout
        # this creates an entry labeled "Data Interval" where the user
        # can enter the desired data interval
        layout.addRow("Data Interval", self.interval_spinbox)
```
> At this point, you can see what the widget looks like by running [this file](./my_plugin/random_data/widget_example.py) inside **`random_data`**. If you want more advanced widgets, check out [`PyQt6`](https://doc.qt.io/qtforpython-6/)'s docs or the [PyQt6 Tutorial](https://www.pythonguis.com/pyqt6-tutorial/).

You'll notice we passed `None` for the description. While this is allowed, users of your plugin will *really* appreciate an explanation of what your item does. Plus, "No description provided" seems a little lackluster. Let's add a description.

### Descriptions

Item descriptions have four sections:
- The **Overview** section provides a brief explanation of what the item does.
- The **Parameters** section explains each parameter on the parameters tab, if any.
- The **Data Recording** section describes the contents of any files/folders the item creates during a sequence, if any.
- The **Visuals** section explains what plots are shown during the sequence, if any.

Fabrial supports two description locations: Python source code and external files.

#### Descriptions from Source Code
Descriptions stored in Python source code use the [`TextDescription`](../../fabrial/utility/descriptions.py) class. Using a `TextDescription` in our widget looks like this:

<sub>Filename: random_data/random_widget.py</sub>
```python
        # --snip--

        ItemWidget.__init__(
            self,
            parameter_widget,
            NAME,
            ICON,
            TextDescription(
                NAME,
                "Records random data on an interval.",
                {"Data Interval": "How often to record data."},
                {"random_data.txt": "The recorded random data."},
                "Plots the random data over time.",
            ),
        )

        # --snip--
```

The resulting description will look something like this:

> Records random data on an interval.
> ## Parameters
>
> - **Data Interval**
>
>   How often to record data.
>
> ## Visuals
>
> Plots the random data over time.
>
> ## Data Recording
>
> Data is written to **Random Data**, which contains:
>
> - **metadata.json**
>
>   Metadata for this sequence step.
>
> - **random_data.txt**
>
>   The recorded random data.

`TextDescription` is best suited for small descriptions that are unlikely to change. For more robust descriptions, we can use the `FilesDescription` class.

#### Descriptions from Files

Descriptions stored in external files use a [`FilesDescription`](../../fabrial/utility/descriptions.py) with an optional [`Substitutions`](../../fabrial/utility/descriptions.py). A description folder must have the following structure:
```
description_folder
├── data_recording.toml
├── overview.md
├── parameters.toml
└── visuals.md
```
Description folders are a combination of [Markdown](https://www.markdownguide.org/basic-syntax/) and [TOML](https://toml.io/en/) files. Adding a description folder to **`random_data`** looks like this:
```
random_data
├── descriptions
│   ├── data_recording.toml
│   ├── overview.md
│   ├── parameters.toml
│   └── visuals.md
└── --snip--
```
Let's walk through the contents of each file.

<sub>Filename: descriptions/overview.md</sub>
```
Records random data on an interval.
```

<sub>Filename: descriptions/parameters.toml</sub>
```
"{{ DATA_INTERVAL }}" = """How often to record data."""
```

<sub>Filename: descriptions/visuals.md</sub>
```
Plots the random data over time.
```
<sub>Filename: descriptions/data_recording.toml</sub>
```
"{{ DATA_FILE }}" = """The recorded random data."""
```

You may notice the weird `{{ DATA_INTERVAL }}` and `{{ DATA_FILE }}` text where the parameter and file names should go. This is where the `Substitutions` class comes in. Fabrial uses [`jinja2`](https://jinja.palletsprojects.com/en/stable/) to perform substitutions for any variable names enclosed in `{{ }}`. If some text is more easily stored in our source code, we can substitute it in from Python. Using a `FilesDescription` and a `Substitutions` in our widget looks like this:

<sub>Filename: random_data/random_widget.py</sub>
```python
        # --snip--

        ItemWidget.__init__(
            self,
            parameter_widget,
            NAME,
            ICON,
            FilesDescription(
                # we provide the absolute path to the descriptions folder
                DIRECTORY.joinpath("descriptions"),
                NAME,
                Substitutions(
                    # notice how the dictionary keys correspond to the
                    # substitutions in the files
                    parameters={"DATA_INTERVAL": "Data Interval"},
                    data_recording={"DATA_FILE": "random_data.txt"},
                ),
            ),
        )

        # --snip--
```

> Although we only use substitutions for the **Parameters** and **Data Recording** files here, all sections support any number of `jinja2` substitutions anywhere in the file.

This code will generate the same description text as in the [Descriptions from Source Code](#descriptions-from-source-code) section.

___

Phew! That was a lot of work. Depending on what your item does, the widget may be the most complicated part. For this tutorial, it definitely is, so good news! It gets easier from here.

The complete widget code is shown below.

<sub>Filename: random_data/random_widget.py</sub>
```python
from pathlib import Path

from fabrial import FilesDescription, ItemWidget, Substitutions
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QDoubleSpinBox, QFormLayout

NAME = "Random Data"
DIRECTORY = Path(__file__).parent
ICON = QIcon(str(DIRECTORY.joinpath("example_icon")))


class RandomDataWidget(ItemWidget):
    """Record random data on an interval; widget."""

    def __init__(self, data_interval: float):
        layout = QFormLayout()
        parameter_widget = QWidget()
        parameter_widget.setLayout(layout)

        ItemWidget.__init__(
            self,
            parameter_widget,
            NAME,
            ICON,
            FilesDescription(
                DIRECTORY.joinpath("descriptions"),
                NAME,
                Substitutions(
                    parameters={"DATA_INTERVAL": "Data Interval"},
                    data_recording={"DATA_FILE": "random_data.txt"},
                ),
            ),
        )

        self.interval_spinbox = QDoubleSpinBox()
        self.interval_spinbox.setMinimum(0.1)
        self.interval_spinbox.setMaximum(1000)
        self.interval_spinbox.setValue(data_interval)
        layout.addRow("Data Interval", self.interval_spinbox)
```