from .....gamry_integration import GAMRY

INITIAL_FREQUENCY = "Initial Frequency (Hz)"
FINAL_FREQUENCY = "Final Frequency (Hz)"
POINTS_PER_DECADE = "Points Per Decade"
AC_VOLTAGE = "AC Voltage (mV rms)"
DC_VOLTAGE = "DC Voltage (V)"
DC_VOLTAGE_REFERENCE = "DC Voltage Reference"
ESTIMATED_IMPEDANCE = "Estimated Z (ohms)"
IMPEDANCE_READER_SPEED = "Impedance Reader Speed"
SELECTED_PSTATS = "Potentiostat(s)"

VS_EREF = "Vs. Eref"
VS_EOC = "Vs. Eoc"

# fails if GamryCOM is not enabled or could not be loaded
try:
    IMPEDANCE_READER_SPEED_DICT: dict[str, int] = {
        "Fast": GAMRY.com_interface().ReadZSpeedFast,
        "Normal": GAMRY.com_interface().ReadZSpeedNorm,
        "Low Noise": GAMRY.com_interface().ReadZSpeedLow,
    }
except Exception:
    IMPEDANCE_READER_SPEED_DICT = dict()


class Headers:
    """Headers for EIS files."""

    # these are tab-separated
    GAMRY_HEADERS = (
        ("EXPLAIN",),
        ("TAG", "EISPOT"),
        ("TITLE", "LABEL", "Potentiostatic EIS", "Test &Identifier"),
        (),
    )
    DATA_HEADERS = (
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


class FileFormat:
    DELIMETER = "\t"
