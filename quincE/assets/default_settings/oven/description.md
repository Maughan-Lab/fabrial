{{ APPLICATION_NAME }} labels temperatures as Celsius, but it does not matter whether the oven actually uses Celsius.

*Settings are loaded the next time {{ APPLICATION_NAME }} launches.*


# General

- **{{ MINIMUM_TEMPERATURE }}**

    The oven's minimum temperature.

- **{{ MAXIMUM_TEMPERATURE }}**

    The oven's maximum temperature.

- **{{ MEASUREMENT_INTERVAL }}**

    How often to measure the physical oven's temperature and setpoint in milliseconds.

- **{{ STABILITY_TOLERANCE }}**

    How far off from the setpoint a temperature can be before it is considered "unstable". For example, if the oven setpoint is 20°C and the temperature is 20.5°C, a tolerance of 0.4°C makes the measurement unstable but a tolerance of 0.5°C or greater than makes the measurement stable.

- **{{ MINIMUM_STABILITY_MEASUREMENTS }}**

    How many consecutive stable measurements must be taken before the oven temperature is considered "stable".

- **{{ STABILITY_CHECK_INTERVAL }}**

    How often to measure the oven's temperature and setpoint for stability.

# Advanced

These settings are based on [minimalmodbus](https://minimalmodbus.readthedocs.io/en/stable/usage.html). They affect how Quincy interacts with the physical oven.

- **{{ TEMPERATURE_REGISTER }}**

    The number of the register where the physical oven's temperature is stored.

- **{{ SETPOINT_REGISTER }}**

    The number of the register where the physical oven's setpoint is stored.

- **{{ NUMBER_OF_DECIMALS }}**

    The number of decimals used when reading from and writing to the oven.
