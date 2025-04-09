# Sequence Runtime
- Each item needs a `run()` method.
- Let the user select a directory to store all data in.
- Add this directory as a parameter passed to items' `run()` method for processes that write to files.
- Iterate through each item in the model and call its `run()` method.
- Have an `sequenceIndexChanged` signal that you can emit so you can highlight the currently running item. This will only work for the first level of the View.
- At the end of the sequence, check if there are any active processes in the QThreadPool, and if so, cancel them before ending.
- Make sure users can pause and cancel the sequence. Also make it possible to skip the current process (which just cancels the current process without ending the sequence).
- The pause button will replace the start button (just like with the old sequence) and cancel and skip will both be menu options.
- Every process needs to implement a `cancel()` and `pause()` method that the sequence runner can call.
- Processes with visuals (i.e. graphs) should create a visual widget that they can modify. The widget will be displayed on the application's third tab.
    - Add a `visual_widget()` method to the Process class that returns either None or a reference to the process' visual widget.
    - If None is returned, no widget gets placed on the third tab.
    - When you implement this, make sure you remove the previous widget from the 3rd tab *before* you delete the process. Otherwise PyQt will try to display a widget that doesn't exist anymore.
- When you start the sequence, you need to disable all editing. This means you also need to close all widget windows by traversing the TreeModel.
- You should probably put all the stuff for running the sequence in a class called SequenceRunner.

# Sequence File Selection
- This should be just below the Sequence Builder.
- One button and one label: the button triggers a folder select window and the label displays the currently selected directory.

# Implement Widgets
- Enable constant temperature recording
- Temperature set
- Temperature modify
- Hold (no temperature data collection)
- Hold (with temperature data collection)
- Electrochemical Impedance Spectroscopy
- Loop
- TODO more items

# Item Description Within Widgets
- All widgets should have a "Description" tab that explains what they do.
- This will require modifying the BaseWidget class.
    - Probably need to change the `to_dict()` and `from_dict()` methods to affect the "Parameters" tab, since that's where the data is stored.
- Some widgets may also need to know what Process type they are tied to, which can be achieved by using a PARAMETER for the class.
    - For example, widgets that record data need to be able to describe to the user what directory data is stored in, but that information will be stored in the Process.

# Remove unnecessary items from the first tab
- sequence, stability check, the graph

# Constant background stability check
- Have Quincy always take samples from the oven to check stability. Compare the current temperature to the current setpoint. Use a progressbar to indicate progress (WOW!!!). Each time the measurement is within tolerances, increment a counter and send a signal with that counter to indicate progress. If a measurement is not within tolerance, set the counter to zero (and send the signal again). Quincy should always be checking stability, since the oven temperature could suddenly dip or spike even if the setpoint doesn't change.
