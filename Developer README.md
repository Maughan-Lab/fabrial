# Adding New Actions to the Sequence Builder
Some general notes
- "Item widgets" are used to display item parameters and descriptions, but they also dictate the behavior of the item itself. For example, the `SUPPORTS_SUBITEMS` parameter of the *widget* dictates whether the *item* can have subitems. The reason for this is convenience. This way, the only things you need to create when implementing a new item (source-code-wise) are the item's widget and process.
- The terms "action" and "item" are used pretty much interchangeably. An "item" is something shown in the TreeView, and an action is what that item does, but they are more or less the same thing.

## Adding a category
*If you are adding an action to an *existing* category, you can ignore this.

- Navigate to **src/sequence_builder/items/**.
    - Create a new folder for your category.
    - Place an empty **\_\_init\_\_.py** file there.
    - Create a file for the category's widget. The name does not really matter, but other categories call this file **category_widget.py**.
        - Subclass `CategoryWidget` (in **base_widget.py**) and override the `DISPLAY_NAME` parameter with the name you want displayed on the category item.
        - Open **item_types.py** and add a new enum member to `ItemType`. The value of the new enum member is the class type of the category widget.
            - Again, the name of the enum member is not super important, but it should correspond to the category name and it must be unique
- Navigate to **initialization/** (sibling directory of **src/**)
    - Create a folder for the category
        - Create a **category.json** file with the following information:
            ```
            {
                "type": "ENUM ENTRY NAME"
            }
            ```
            where `"ENUM ENTRY NAME"` is the same name you used as the enum member in **item_types.py**.
- At this point, if you try to run Quincy, you should see your category appear. It will just have no subitems.
- Navigate to **item_descriptions/** and create a folder there for your category. Actions will use this folder for their item descriptions.

## Adding an action
- Navigate the **src/sequence_builder/items/[category you're adding to]/**
    - Create a folder for your action.
        - Add an empty **\_\_init\_\_.py** file.
        - Add a file for the item's widget (other items call this **widget.py**).
            - If the widget has modifiable parameters, you should also create a file to store the names of those parameters (as used in a dictionary). Other items call this **encoding.py**.
                - This just makes it easy for the widget and process to use the same names when creating/reading dictionaries.
            - Subclass `BaseWidget` (**src/sequence_builder/items/base_widget.py**), overriding:
                - `PROCESS_TYPE`
                    - The class type of the item's associated process, which gets created in the next step.
                - `ICON`
                    - The name of the icon file in **icons/internal/**.
                    - Optional if you want to use the default icon.
                - `__init__()`
                    - You need to initialize the widget. This includes its contained data as well as the item description.
                    - Make sure to call the base method.
                - `to_dict()`
                    - Convert all of the widget's data into a JSON-friendly dictionary.
                    - You should be able to reconstruct the widget from this dictionary.
                    - This is where you will probably use the names in **encoding.py**.
                - `from_dict()`
                    - This is a class method.
                    - Build the widget from a JSON-friendly dictionary (i.e. the same dictionary format returned by `to_dict()`).
                    - This is how drag-and-drop works: the model just turns the widgets into strings and then reconstructs them.
        - Add a file for the item's process (other items call this **process.py**).
            - You should use the same names from **encoding.py** when accessing the process' data.
            - Subclass `Process` (**src/classes/process.py**), overriding:
                - `WIDGET_TYPE`
                    - The type of the data visualization widget used by the process.
                    - Only necessary if your process has an associated widget.
                - `__init__()`
                    - Call the base method, then initialize any other data.
                - `run()`
                    - The sequence runner will call this method after creating a process instance. It is allowed to do anything, you just need to make sure to frequently call `wait()` so you don't freeze the application.
- In **src/sequence_builder/items/item_types.py**, edit the `ItemType` enum to have an entry for your action's widget.
- Navigate to **initialization/[category you are adding to]/**
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
        - "ENUM ENTRY NAME" is the same name you used as the enum member in **item_types.py**
        - The contents of "linked-widget-data" are dictated by the widget's data encoding. The values supplied here serve as the widget's default values.
- Create an item description file in **item_descriptions/[item category]/**.
    - The file format is Markdown (.md).*
        - The text is rendered as Markdown *regardless of whether you mean to write Markdown*.
    - If the item description is really small, you can just set it in the widget's `__init__()` method instead of creating a file.
    - You can also use Jinja substitutions to substitute text into the item description at runtime using the widgets `set_description_text_from_file()` method
        - For example, "{{ name }}" gets replaced with some other text as long as "name" is an entry in the function's input dictionary.
        - If you're confused, look up Python's Ninja2 module.