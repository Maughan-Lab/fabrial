import csv
import time
from io import TextIOWrapper

from .. import Files
from .datetime import get_datetime


def create_temperature_file(filepath: str) -> TextIOWrapper:
    """
    Create a CSV file that records data in the following format:

    [seconds since start],[datetime],[temperature (degrees C)]

    The header is written automatically.

    :param filepath: The path to the file to create. If the file already exists, it will be
    overwritten. The file is opened in write mode and is line buffered.
    """
    HEADERS = Files.Process.Headers
    file = open(filepath, "w", 1, newline="")
    csv.writer(file).writerow(
        [HEADERS.Time.TIME, HEADERS.Time.TIME_DATETIME, HEADERS.Oven.TEMPERATURE]
    )
    return file


def record_temperature_data(
    file: TextIOWrapper, start_time: float, temperature: float | None
) -> float:
    """
    Record the time since start, datetime, and temperature in the provided file.

    :param file: The CSV file to write to.
    :param start_time: The **Process**'s start time.
    :param temperature: The temperature being recorded.

    :returns: The number of seconds since the **Process** started.
    """
    current_time = time.time()
    time_since_start = current_time - start_time
    csv.writer(file).writerow([time_since_start, get_datetime(current_time), str(temperature)])
    return time_since_start
