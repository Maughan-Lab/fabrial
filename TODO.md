# Fix Fabrial (GAHHH)
- Update Gamry software on the laptop and run tests.
- When that doesn't work, email support again and ask for help.

# Fixing Fabrial for Modularization

## Disable plugins when they fail to load.
Do it :D

## The Oven
- The oven should not be a constant part of the application. My current idea is to put manual control of the oven in a separate application that shares source code with the rest of Fabrial.
    - The oven should not be monitoring its own temperature, that should be the responsibility of some widget/task.
    - The oven shouldn't have signals. If you want to monitor its connection, just check it when you read the temperature and setpoint.
    - The oven should not be stabilizing itself. That is the responsibility of the sequence.

## Some Sequence Steps
- Oven-based sequence steps should create a new oven instead of referencing a global variable.
- The oven stabilization algorithm needs to be rewritten to use the 

## The Sequence
- Figure out how to record the oven setpoint in every process, even without a global oven instance.
    - The solution to this is just to add a `Record Temperature` sequence step. Users will have to manage the rest.

## Consistency
- "instrument" $\to$ "device"

## Protocols
- Make a `Protocol` class for devices. This will make your life easier.

## Sequence
- Disable the sequence view when the sequence is running.

## Application Settings
- A lot of application-level settings will need to be removed (looking at you oven settings). Most of these can be put into sequence items.
- You should use TOML files instead of JSON files for default settings.
- Add an optional entry point, `settings_widget() -> QWidget` for plugins. Add the result to the settings menu as a new tab.
- You should have a general `Plugins` tab.
    - It will have a section for `Global Plugins` and `Local Plugins`. The user can enable/disable items for a plugin. In the `Local Plugins` section, they can also remove the plugin (which just deletes the folder).

## Documentation
- It needs to be easier for newbies to add items to the sequence. You need a fully documented walkthrough. You should show the user how to implement a custom external item , step by step, explaining everything. You'll need links to outside sources to explain things like `PyQt` and `asynchio`, but you also need to be hand-wavy enough that the user doesn't get stuck in the details and can just follow what you are telling them to do. You can assume some `PyQt` experience.
- Write some guides:
    - Installation guide.
    - Basic usage guide (don't need to go super in depth because of the documentation on individual items).
