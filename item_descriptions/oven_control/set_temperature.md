Set the oven's temperature and wait for it to stabilize. Record the oven's temperature every {{ MEASUREMENT_INTERVAL }} seconds.

# Parameters
- **Temperature** - the temperature to set the oven to.

# Visuals
The oven's temperature over time is shown graphically.

# Data Recording
Data is written into `{{ DIRECTORY_NAME }}/[datetime of start]`. The directory contains:
- `{{ TEMPERATURE_FILE }}` - oven temperatures and their timestamps.
- `{{ METADATA_FILE }}` - the start and end times timestamps of the action.
