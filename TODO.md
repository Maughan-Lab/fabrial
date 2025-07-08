# Fix Quincy (GAHHH)
- Update Gamry software on the laptop and run tests.
- When that doesn't work, email support again and ask for help.

# Fixing Quincy for Modularization
## Packaging
- Use the `--add-data` option to copy files instead of doing it manually.

## Interface Stuff
Use `Protocol` instead of ABC. Try to minimize inheritance and use interfaces instead.

## Sequence View
- All human-written files should use `TOML`
- Make the `TreeItem` class the thing that gets saved to a file, not the widget.
    - This involves your `serde` code.
- Change how the SequenceOptions model initialization works
    - All human-written JSON files should be converted to TOML files.

## Items
- *Items* should create the process, not the SequenceRunner. i.e., the SequenceRunner should call something like `make_process()` on the item, then use that process.
    - With this, instead of passing the root item to the sequence runner, just pass a collection of `Process`s. For the loop, this may involve recursion.
- Items and widgets should use `from_dict()` and `as_dict()` methods for serde.

## The Oven
- The oven should not be a constant part of the application. My current idea is to put manual control of the oven in a separate application that shares source code with the rest of Quincy.
    - The oven should not be monitoring its own temperature, that should be the responsibility of some widget/task.
    - The oven shouldn't have signals. If you want to monitor its connection, just check it when you read the temperature and setpoint.
    - The oven should not be stabilizing itself. That is the responsibility of the sequence.

## Some Sequence Steps
- Oven-based sequence steps should create a new oven instead of referencing a global variable.
- The oven stabilization algorithm needs to be rewritten to use the 

## The Sequence
- Implement a "simultaneous" step that uses `asyncio` to run two things concurrently.
    - To support this, all `run()` methods must be declared as `async`. Also, `wait()` must be `async` and it should call `asynchio.sleep(0)`.
- Add a `wait_until()` method.
- Use exceptions to cancel and skip things.
- Debate whether the pause button is still necessary.
    - If you keep pause capabilities, remove the "error pause" state.
- Stop calling `process_events()`. You can probably block the `QThread`'s event loop—you'll still be able to send signals, just not receive them.

## Communication with the Sequence
- Make the dialog system better. Try to still use `QMessageBox`. You should be able to do something like this:
```python
self.send_query("Message text", {"First Button Text": value1, "Second Button Text": value2})
response = self.wait_for_response() # `response` has the same type as value1 and value2
match response:
    case value1:
        # do something for value1
    case value2:
        # do something else
    case _:
        # this is probably an error
```

## Multi-Level Cancellations
If you are in a loop/other nested sequence step, you should be able to cancel the outer item or *any* of the inner items. There should be a cancel button with a combobox next to it. The combobox should show the available "depths" you can cancel. For example, if you have something like this:
```
-loop 1
    - loop 2
        - loop 3
            - some item
```
you should be able to cancel `loop 1`, `loop 2`, `loop 3`, or `some item` by selecting `1`, `2`, `3`, or `4` from the combobox, respectively. To do this, you need to keep track of the current depth using a stack. The stack contains references to `Task`s corresponding to the depth. When you cancel a `Task`, you cancel all tasks above it first.

All nested tasks will need to call some method on the `ProcessRunner` that runs a list of `Process`es and increments the depth counter. When the process list finished, the counter should be decremented. This counter could be automatic by using the length of the stack.

## Error Logging
- Instead of showing the whole error in a dialog that can get cut off, record the error in a logging file, then show an error dialog that says something like "Quincy encountered a fatal error and needs to close".

## Constants
- Put the `Files` module inside a `constants` module, rename it to `files`, and use `__init__.py` files to handle everything.

## Consistency
- Make sure you aren't importing functions, just the module containing them.
- Make all `files` modules snake case.
- Keep the original comment style used for Quincy, don't change to Rust style.
- Mark methods as "overridden" or "implementation".
- "instrument" $\to$ "device"
- Use more `__init__.py` files for re-exporting.

## Protocols
- Make a `Protocol` class for devices. This will make your life easier.

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
