# TODO
## Add a delete button to get rid of items in the sequence
- The title says it all
## Alphabetize the initializer for the options tree
- On the `TreeModel.from_file()` method, alphabetize the items. You will probably need to implement an `sort_children()` method on the TreeItem.
## Copy/Paste Via the Keyboard
- If it's not a huge pain, make it so that you can copy and paste with Ctrl+C and Ctrl+V in the TreeModel
- Call `mimeData()` and `dropMineData()` to implement this. You'll need a global variable to store the QMimeData instance.
- This will be implemented on the model, so both views will have access to it. You'll want to disable cutting and pasting on one of the views so users can only copy *from* it and not *to* it.
## Base class for ModelView
- Add a base class with support for copy, cut, paste, and delete. There should be buttons that get shown or hidden based on whether copy/cut/paste/delete is enabled.

## Implement Widgets
- Enable constant temperature recording
- Temperature set
- Temperature modify
- Hold (no temperature data collection)
- Hold (with temperature data collection)
- Electrochemical Impedance Spectroscopy
- TODO more items

# Implementing the Runtime Sequences
- Implement `run()` for all the items.
- Come up with a system for interacting with the graph (only one process will use it at a time)
- You will probably need to pass a QThreadPool to `run()` so that background processes can add themselves to the pool and run all the time.

# Constant background stability check
- Have Quincy always take samples from the oven to check stability. Compare the current temperature to the current setpoint. Use a progressbar to indicate progress (WOW!!!). Each time the measurement is within tolerances, increment a counter and send a signal with that counter to indicate progress. If a measurement is not within tolerance, set the counter to zero (and send the signal again). Quincy should always be checking stability, since the oven temperature could suddenly dip or spike even if the setpoint doesn't change.