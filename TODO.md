# Implement Widgets
- Enable constant temperature recording
- Hold (no temperature data collection)
- Hold (with temperature data collection) (subclass of above)
- Electrochemical Impedance Spectroscopy
    - Similarly to how you have an `Oven` class for the physical oven, you should make a `Potentiostat` class that gets created each time an **EIS** action is run, for each potentiostat. This means you can abstract things like running EIS.
- Loop
- TODO more items

# Remove unnecessary items from the first tab
- sequence, stability check, the graph

# Constant background stability check
- Have Quincy always take samples from the oven to check stability. Compare the current temperature to the current setpoint. Use a progressbar to indicate progress (WOW!!!). Each time the measurement is within tolerances, increment a counter and send a signal with that counter to indicate progress. If a measurement is not within tolerance, set the counter to zero (and send the signal again). Quincy should always be checking stability, since the oven temperature could suddenly dip or spike even if the setpoint doesn't change.

# Allow users to edit the temperature and setpoint registers of the oven, and the min and max setpoints
- The oven already reads from a file, but you need to be able to edit that from within the application.
- You should save the data to a file when the widget you use to edit the settings is closed. Use `Oven.save_settings()`.
- This should be a button or menu option the user can click to open up a widget. The widget should let them change the value of the temperature and setpoint registers. It should also save the new values to a file so the change carries over.
- The changes do not take effect until the next time Quincy is launched.
- The widget also needs a description tab to explain what the registers mean.

# Add an exception hook to catch any uncaught exceptions
It's in the title, look up how to do this