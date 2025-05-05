# Adding New Items to the Sequence Builder
Some general notes
- "Item widgets" are used to display item parameters and descriptions, but they also dictate the behavior of the item itself. For example, the `allowed_to_create()` static function of the *widget* dictates whether the *item* can be created. The reason for this is convenience. This way, the only things you need to create when implementing a new item (source-code-wise) are the item's widget and process. The item's properties are based on these two.
- The terms "action" and "item" are used pretty much interchangeably. An "item" is something shown in the TreeView, and an action is what that item does, but they are more or less the same thing.

## Adding a category
**Note:** If you are adding an action to an *existing* category, you can skip this.

- Navigate to **src/sequence_builder/items**.
    - Create a new folder for your category.
    - Create an **\_\_init\_\_.py** file there.
    - Create a file for the category's widget. The name does not really matter, but other categories call this file **category_widget.py**.
        - Subclass `CategoryWidget` (in **base_widget.py**).
        - Open **item_types.py** and add a new enum member to `ItemType`. The value of the new enum member is the class type of the category widget.
            - The name of the enum member is not super important, but it should correspond to the category name and it must be unique.
- Navigate to **item_initialization** (sibling directory of **src**)
    - Create a folder for the category.
        - Create a **category.json** file with the following information:
            ```
            {
                "type": "ENUM ENTRY NAME"
            }
            ```
            where `ENUM ENTRY NAME` is the same as the variable name you used for the enum member in **item_types.py**.
- At this point, if you try to run Quincy, you should see your category appear. It will just have no subitems.
- Navigate to **item_descriptions** and create a folder there for your category. Items will use this folder for their item descriptions.

## Creating a description
- Create a folder for your item in **item_descriptions/[item category]**.
    - The file format is **Markdown (.md)**.
        - The text is rendered as Markdown *regardless of whether you mean to write Markdown*.
    - The folder contains files for each description section:
        - **overview.md**
            - An overview of what the item does.
        - **parameters.md**
            - Lists the parameters the item takes in and explains what they mean.
        - **visuals.md**
            - Explains what visuals are shown by the process (i.e. on the graph), if any.
            - If there are no visuals, **this file is optional**.
        - **data_recording.md**
            - Lists the files the process writes data to and describes what those files contain.
            - The **metadata.csv** file is already listed for you and does not need to be documented.
            - If the process does not record data other than metadata, this **file is optional**.
    - You can use jinja substitutions to substitute text into the item description at runtime.
        - For example, the text `{{ name }}` gets replaced by the text the substitution dictionary with the key `name`. If you use substitutions, the substitution dictionary must include the corresponding key.
        - If you're confused, look up Python's `Jinja2` module. I learned it from [this example](https://www.geeksforgeeks.org/getting-started-with-jinja-template/)
        (please god let this link still be valid).
        - More on this in the [Adding an action](#adding-an-action) section.

## Adding an action
- Navigate the **src/sequence_builder/items/[category you're adding to]**
    - Create a folder for your action.
        - Import this folder from the category's **\_\_init\_\_.py** file.
        - Add an **\_\_init\_\_.py** file.
        - Add a file for the item's widget (other items call this **widget.py**).
            - Import this file from the previous **\_\_init\_\_.py** file (this makes a future step easier).
            - If the widget has modifiable parameters, you should also create a file to store the names of those parameters (as used in a dictionary). Other items call this **encoding.py**.
                - This just makes it easy for the widget and process to use the same names when creating/reading dictionaries.
            - Subclass `AbstractBaseWidget` (**src/sequence_builder/items/base_widget.py**). You must implement:
                - `to_dict()`
                    - Convert all of the widget's data into a JSON-friendly dictionary.
                    - You should be able to reconstruct the widget from this dictionary.
                    - This is where you will probably use the names in **encoding.py**.
                - `from_dict()`
                    - This is a class method (`@classmethod`).
                    - Build the widget from a JSON-friendly dictionary (i.e. the same dictionary format returned by `to_dict()`).
                    - This is how drag-and-drop works: the model just turns the widgets into JSON strings and then reconstructs them.
            - To set the item description, supply the `description_info` argument to `__init__()`. This argument is a `DescriptionInfo` object (**src/classes/descriptions.py**) that explains how to generate the description.
                - `category_folder`
                    - The folder inside **item_descriptions** that contains the item description folder. For example, **temperature**.
                - `item_folder`
                    - The folder that contains the description files. For example, **set_temperature**.
                - `data_folder`
                    - The name of the process' data folder, as returned by `process.directory_name()`. For example, **Set Temperature**.
                - `substitutions`
                    - A `DescriptionInfo.Substitutions` object that contains dictionaries for jinja substitutions for each file. If the description does not use jinja substitutions, **this is optional**.

        - Add a file for the item's process (other items call this **process.py**).
            - You should use the same names from **encoding.py** when accessing the process' data.
            - Subclass either `AbstractForegroundProcess` or `AbstractBackgroundProcess` (**src/classes/process.py**), depending on whether the process runs in the foreground or the background. You must implement:
                - `directory_name()`
                    - This is a static method (`@staticmethod`).
                    - This dictates the name of the directory the process writes data to. All processes must have a data directory because they all record metadata in a **metadata.csv** file.
                    - The process runner will take care of the full file path and process number, so use something like **Set Temperature** instead of **C:/Users/.../Set Temperature**.
                - `run()`
                    - The sequence runner will call this method after creating a `Process` instance. It is allowed to do anything, you just need to make sure to frequently call `wait()` so you don't freeze the application.
- In **src/sequence_builder/items/item_types.py**, edit the `ItemType` enum to have an entry for your action's widget.
- This is where modifying the **\_\_init\_\_.py** files comes in handy, as you don't have to provide a full import path to the widget file.
- Navigate to **item_initialization/[category you are adding to]**
    - Create **.json** file for your action containing the following info:
        ```
        {
            "type": "ENUM ENTRY NAME"
            "linked-widget-data": {
                "DATA ITEM 1": value
                "DATA ITEM 2": value
                ...
            }
        }
        ```
        where
        - `ENUM ENTRY NAME` is the same as the variable name you used for the enum member in **item_types.py**
        - The contents of `linked-widget-data` are dictated by the widget's data encoding. The values supplied here serve as the widget's default values.
