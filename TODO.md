# Fix deletion issue
- When selecting two items from the bottom-up, then deleting, the new selected index is wrong (it's above instead of below the last selected item)

# Implement Widgets
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

# Make all custom widgets take a parent argument
- The title says it all