# TODO
## Add a delete button to get rid of items in the sequence
- The title says it all
## Copy/Paste Via the Keyboard
- If it's not a huge pain, make it so that you can copy and paste with Ctrl+C and Ctrl+V in the TreeModel

## Implement Widgets
- Enable constant temperature recording
- Temperature set
- Temperature modify
- Hold (no temperature data collection)
- Hold (with temperature data collection)
- Electrochemical Impedance Spectroscopy
- 

# Implementing the Runtime Sequences
- Implement `run()` for all the items.
- Come up with a system for interacting with the graph (only one process will use it at a time)
- You will probably need to pass a QThreadPool to `run()` so that background processes can add themselves to the pool and run all the time.