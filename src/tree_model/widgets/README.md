# Adding new sequence options
Follow all of the steps below in order to add a new sequence option.

## Define the data encoding
1. In the **data_encodings** directory, create a new Python file for the sequence option.
2. Create string constants which correspond to the name of each data member for the option.

## Define the option's template file
*TODO*

## Add the widget
1. In the **widgets** directory, create a new Python file for the sequence option's widget. I recommend using the same name as the data encoding file.
2. The new widget must inherit from `BaseWidget` contained in **base.py**. It must implement the `from_dict()` and `to_dict()` methods.
    1. `from_dict()` creates a new widget instance from a JSON-style dictionary.
    2. `to_dict()` creates a JSON-style dictionary from the widget's contained data.

    These methods allow the sequence option to be dragged and dropped in the ModelView, and to be saved in files. When implementing them, you should use the constants defined in the option's data encoding file. I like to import the encoding file as `DATA` for consistency across options.

## Add the option to the initialization file
Add the option, encoded in JSON format, to the **options.json** file. It must be placed in the `children` entry of the base-level item. In most cases, the option should have no children. The names of the data members for the option must match those defined in the option's data encoding file.

This causes the option to show up in the list of options the user can choose from when Quincy runs.
