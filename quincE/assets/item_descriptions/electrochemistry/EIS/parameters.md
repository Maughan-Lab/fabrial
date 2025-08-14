- **{{ POTENTIOSTATS }}**

    The potentiostats to run EIS with. These are potentiostat identifiers, which should be somewhere
    on the physical devices.

- **{{ DC_VOLTAGE }}**

    The DC voltage offset in Volts.

    - **{{ VS_EREF }}**

        The voltage is vs. the reference.

    - **{{ VS_EOC }}**

        The voltage is vs. the open-circuit voltage.

- **{{ INITIAL_FREQUENCY }}**

    The starting frequency of the frequency sweep in Hz.

- **{{ FINAL_FREQUENCY }}**

    The finishing frequency of the frequency sweep in Hz.

- **{{ POINTS_PER_DECADE }}**

    Affects the distance between and number of frequencies over the sweep.

- **{{ AC_VOLTAGE }}**

    The AC voltage for the sweep in millivolts.

- **{{ ESTIMATED_IMPEDANCE }}**

    The initial guess for the sample's impedance in Ohms.
