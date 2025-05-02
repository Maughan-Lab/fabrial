{{ OVERVIEW_TEXT }}

# Parameters
{{ PARAMETERS_TEXT }}

# Visuals
{{ VISUALS_TEXT }}

# Data Recording
{% if DIRECTORY_NAME != "" %}

Data is written to **{{ DIRECTORY_NAME }}**. This directory contains:
- **{{ METADATA_FILE }}**

    Metadata for the process. By default, it contains the following:

    - Start date and time
    - End date and time
    - Duration in seconds
    - Oven setpoint (measured at the end of the process)

{{ DATA_RECORDING_TEXT }}

{% else %}

Error: directory name was not provided.

{% endif %}