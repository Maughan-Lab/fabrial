# Fix Quincy (GAHHH)
- Update Gamry software on the laptop and run tests.
- When that doesn't work, email support again and ask for help.

# Fixing Quincy for Modularization

## Items
- *Items* should create the process, not the SequenceRunner. i.e., the SequenceRunner should call something like `make_process()` on the item, then use that process.
    - With this, instead of passing the root item to the sequence runner, just pass a collection of `Process`s. For the loop, this may involve recursion.

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
- Use exceptions to cancel and skip things.
    - Should we even support skipping?
- Debate whether the pause button is still necessary.
    - If you keep pause capabilities, remove the "error pause" state.
    - If you use `asyncio.sleep(0)`, you should call `time.sleep()` while paused so you don't switch back to the process.
- Stop calling `process_events()`. You can probably block the `QThread`'s event loop—you'll still be able to send signals, just not receive them.
- Figure out how to record the oven setpoint in every process, even without a global oven instance.
    - The solution to this is just to add a `Record Temperature` sequence step. Users will have to manage the rest.

## Communication with the Sequence
- Make the dialog system better. Try to still use `QMessageBox`. You should be able to do something like this:
```python
response = self.wait_for_response("Message text", {0: "First Button Text", 1: "Second Button Text"})
# we have to use integers so that it's a single type
# no, it can't be a list because then it's not obvious what corresponds to what
# no, it shouldn't be {text: value} because the values need to be unique. It doesn't matter if the button text is unique; if it isn't, that's a user error
match response:
    case 0:
        # do something
    case 1:
        # do something else
    case _:
        # this is probably an error
```
You can use a custom `QPushButton` and `addButton(button, QMessageBox.ButtonRole.NoRole)` + `clickedButton()` to add buttons and associate a value.

## Error Logging
- Instead of showing the whole error in a dialog that can get cut off, record the error in a logging file, then show an error dialog that says something like "Quincy encountered a fatal error and needs to close".

## Consistency
- "instrument" $\to$ "device"

## Protocols
- Make a `Protocol` class for devices. This will make your life easier.

### Avoid pyqtSignals(?)
- See if it would be better to use `Queue`s instead of signals to send data across the thread boundary.

## Application Settings
- A lot of application-level settings will need to be removed (looking at you oven settings). Most of these can be put into sequence items.
- You should use TOML files instead of JSON files for default settings.
- Add an optional entry point, `settings_widget() -> QWidget` for plugins. Add the result to the settings menu as a new tab.

## Documentation
- It needs to be easier for newbies to add items to the sequence. You need a fully documented walkthrough. You should show the user how to implement a custom external item , step by step, explaining everything. You'll need links to outside sources to explain things like `PyQt` and `asynchio`, but you also need to be hand-wavy enough that the user doesn't get stuck in the details and can just follow what you are telling them to do. You can assume some `PyQt` experience.
- Write some guides:
    - Installation guide.
    - Basic usage guide (don't need to go super in depth because of the documentation on individual items).
