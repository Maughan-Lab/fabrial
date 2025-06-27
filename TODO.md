# Fix Quincy (GAHHH)
- Update Gamry software on the laptop and run tests.
- When that doesn't work, email support again and ask for help.

# Fixing Quincy for Modularization
## Packaging
- Use the `--add-data` option to copy files instead of doing it manually.

## Sequence View
- All human-written files should use 
- Make the `TreeItem` class the thing that gets saved to a file, not the widget.
    - This involves `jsonpickle` and `dataclass_wizard`.
- Change how the SequenceOptions model initialization works
    - All human-written JSON files should be converted to TOML files.
        - This will require a combination of `tomllib` and `jsonpickle`. Use `jsonpickle.Unpickler().restore()` to convert from a dictionary to a Python object. Reuse the unpickler when you can.

## Items
- *Items* should create the process, not the SequenceRunner. i.e., the SequenceRunner should call something like `make_process()` on the item, then use that process.
    - With this, instead of passing the root item to the sequence runner, just pass a collection of `Process`s. For the loop, this may involve recursion.
- All constant attributes for a widget/process should be class attributes, not `@staticmethod`s. To enforce this with abstract classes, use something like
    ```python
    class Base(ABC):
        @property
        @abstractmethod
        def A(self) -> int: ...  # means no implementation here


    class Child(Base):
        A = 5
        pass
    ```
    - This includes things like the process directory and the widget's icon name and description info.
        - The only thing left in the widget constructor should be the layout and the display name.
- Items and widgets should use the `DataCrate` system for serialization/deserialization.

## The Oven
- The oven should not be a constant part of the application. My current idea is to put manual control of the oven in a separate application that shares source code with the rest of Quincy.
    - The oven should not be monitoring its own temperature, that should be the responsibility of some widget.
    - The oven shouldn't have signals. If you want to monitor its connection, just check it when you read the temperature and setpoint.
    - The oven should not be stabilizing itself. That is the responsibility of the sequence.

## Some Sequence Steps
- Oven-based sequence steps should create a new oven instead of referencing a global variable.
- The oven stabilization algorithm needs to be rewritten to use the 

## The Sequence
- Implement a "simultaneous" step that uses `asynchio` to run two things concurrently.
    - To support this, all `run()` methods must be declared as `async`. Also, `wait()` must be `async` and it should call `asynchio.sleep(0)`.
- Add a `wait_until()` method.
- Use exceptions to cancel and skip things.
- Debate whether the pause button is still necessary.
    - If you keep pause capabilities, remove the "error pause" state.
- Polish up the system for communicating with processes via user input.

## Constants
- Put the `Files` module inside a `constants` module, rename it to `files`, and use `__init__.py` files to handle everything.

## Consistency
- Make sure you aren't importing functions, just the module containing them.
- Make all `files` modules snake case.
- Keep the original comment style used for Quincy, don't change to Rust style.
- Mark methods as "overridden" or "implementation".
- "instrument" $\to$ "device"
- Use more `__init__.py` files for re-exporting.

## Abstract Classes
- Make an abstract class for devices. This will make your life easier.

## Legacy Code
- Check the `status.py` enum file to see if you can remove stuff.

## External Items
- Add support for user-added sequence items. It looks like the code for these has to reside within `src` for them to be able to access the rest of the codebase, but it could be in a folder like `user_items`.

## Avoid Locks
- See if you can use a build-in `Event` object to synchronize between `QThread`s.

## Application Settings
- A lot of application-level settings will need to be removed (looking at you oven settings). Most of these can be put into sequence items.
- You should use TOML files instead of JSON files for default settings.

## Documentation
- It needs to be easier for newbies to add items to the sequence. You need a fully documented walkthrough. You should show the user how to implement a custom external item , step by step, explaining everything. You'll need links to outside sources to explain things like `PyQt` and `asynchio`, but you also need to be hand-wavy enough that the user doesn't get stuck in the details and can just follow what you are telling them to do. You can assume some `PyQt` experience.
- Write some guides:
    - Installation guide.
    - Basic usage guide (don't need to go super in depth because of the documentation on individual items).
