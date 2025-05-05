INITIAL_FREQUENCY = "Initial Frequency (Hz)"
FINAL_FREQUENCY = "Final Frequency (Hz)"
POINTS_PER_DECADE = "Points Per Decade"
AC_VOLTAGE = "AC Voltage (mV rms)"
DC_voltage = "DC Voltage (V)"
AREA = "Sample Area (cm^2)"
ESTIMATED_IMPEDANCE = "Estimated Z (ohms)"
SELECTED_PSTATS = "Potentiostat(s)"


class Headers:
    """Headers for EIS files."""

    # these are tab-separated
    EXPERIMENT_HEADERS = (
        ("EXPLAIN",),
        ("TAG", "EISPOT"),
        ("TITLE", "LABEL", "Potentiostatic EIS", "Test &Identifier"),
        ("ZCURVE", "TABLE"),
        (
            "",  # empty string to start line with tab
            "Pt",
            "Time",
            "Freq",
            "Zreal",
            "Zimag",
            "Zsig",
            "Zmod",
            "Zphz",
            "Idc",
            "Vdc",
            "IERange",
        ),
        ("", "#", "s", "Hz", "ohm", "ohm", "V", "ohm", "°", "A", "V", "#"),
    )
    # EXPERIMENT_HEADER = (
    #     "EXPLAIN\n"
    #     "TAG\tEISPOT\n"
    #     "TITLE\tLABEL\tPotentiostatic EIS\tTest &Identifier\n"
    #     "ZCURVE\tTABLE\n"
    #     "\tPt\tTime\tFreq\tZreal\tZimag\tZsig\tZmod\tZphz\tIdc\tVdc\tIERange\n"
    #     "\t#\ts\tHz\tohm\tohm\tV\tohm\t°\tA\tV\t#\n"
    # )


class Filenames:
    FILE_BASE = "potentiostatic_eis ({}).DTA"


class FileFormat:
    DELIMETER = "\t"
