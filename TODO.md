# Implement Widgets
- Electrochemical Impedance Spectroscopy
    - Similarly to how you have an `Oven` class for the physical oven, you should make a `Potentiostat` class that gets created each time an **EIS** action is run, for each potentiostat. This means you can abstract things like running EIS.
    - This is partially complete. You can create a Potentiostat through the Gamry interface.
## Instructions
Update the instructions for implementing new items

# Allow users to edit the temperature and setpoint registers of the oven, and the min and max setpoints, and the stability parameters
- The oven already reads from a file, but you need to be able to edit that from within the application.
- You should save the data to a file when the widget you use to edit the settings is closed. Use `Oven.save_settings()`.
- This should be a button or menu option the user can click to open up a widget. The widget should let them change the value of the temperature and setpoint registers. It should also save the new values to a file so the change carries over.
- The changes do not take effect until the next time Quincy is launched.
- The widget also needs a description tab to explain what the registers mean.

# Editable settings
- In addition to the oven settings, let the user change:
    - Whether to show a dialog when the data directory for the sequence is not empty.
    - Whether Gamry is enabled.

# Enable/Disable Gamry
- Let the user enable/disable Gamry support in Quincy.
- If Gamry is enabled and Quincy cannot load it, prompt the user to either disable Gamry or abort opening Quincy.
- If Gamry is disabled, remove the Gamry category entirely from the options treeview. Also, ensure that all Gamry-related items are not shown in the application. You probably need to add a method to the `BaseWidget` class that dictates whether the widget can be created and displayed.
