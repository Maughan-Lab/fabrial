INITIAL_FREQUENCY = "initial-frequency"
FINAL_FREQUENCY = "final-frequency"
POINTS_PER_DECADE = "points-per-decade"
AC_VOLTAGE = "AC-voltage"
DC_voltage = "DC-voltage"
AREA = "area"
ESTIMATED_IMPEDANCE = "estimated-impedance"


class Headers:
    GAMRY_HEADER = (
        "EXPLAIN\n"
        "TAG\tEISPOT\n"
        "TITLE\tLABEL\tPotentiostatic EIS\tTest &Identifier\n"
        "ZCURVE\tTABLE\n"
        "\tPt\tTime\tFreq\tZreal\tZimag\tZsig\tZmod\tZphz\tIdc\tVdc\tIERange\n"
        "\t#\ts\tHz\tohm\tohm\tV\tohm\t°\tA\tV\t#\n"
    )
    # TODO


class Filenames:
    # TODO
    pass
