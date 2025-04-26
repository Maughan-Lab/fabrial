Increment the oven's temperature and wait for it to stabilize. Record the oven's temperature every {{ MEASUREMENT_INTERVAL }} ms.

# Parameters
- **Setpoint Increment** - the amount to increment the setpoint by.

# Visuals
The oven's temperature over time is shown graphically.

# Data Recording
Data is written into `[#] {{ DIRECTORY_NAME }}/`. The directory contains:
- `{{ TEMPERATURE_FILE }}` - oven temperatures and their timestamps.
- `{{ METADATA_FILE }}` - default items + the selected setpoint.
