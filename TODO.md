# Fix Fabrial (GAHHH)
- Update Gamry software on the laptop and run tests.
- When that doesn't work, email support again and ask for help.

# Fixing Fabrial for Modularization

## Application Settings
- Add an optional entry point, `settings_widget() -> QWidget` for plugins. Add the result to the settings menu as a new tab.
- You should have a general `Plugins` tab.
    - It will have a section for `Global Plugins` and `Local Plugins`. The user can enable/disable items for a plugin. In the `Local Plugins` section, they can also remove the plugin (which just deletes the folder).
- You also need a tab for the `Sequence` settings, which is just the Don't Show Again Dialog
