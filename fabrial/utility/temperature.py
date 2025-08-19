import csv
import time
from io import TextIOWrapper

from ..constants.paths.process import headers
from .datetime import get_datetime


def create_temperature_file(filepath: str) -> TextIOWrapper:
    """
    Create a CSV file that records data in the following format:

    [seconds since start],[datetime],[temperature (degrees C)]

    The header is written automatically.

    Parameters
    ----------
    filepath
        The path to the file to create. If the file already exists, it will be overwritten. The file
        is opened in write mode and is line buffered.
    """
    file = open(filepath, "w", 1, newline="")
    csv.writer(file).writerow(
        [headers.time.TIME, headers.time.TIME_DATETIME, headers.oven.TEMPERATURE]
    )
    return file


def record_temperature_data(
    file: TextIOWrapper, start_time: float, temperature: float | None
) -> float:
    """
    Record the time since start, datetime, and temperature in the provided file.

    Parameters
    ----------
    file
        The CSV file to write to.
    start_time
        The `Process`'s start time.
    temperature
        The temperature being recorded.

    Returns
    -------
    The number of seconds since the `Process` started.
    """
    current_time = time.time()
    time_since_start = current_time - start_time
    csv.writer(file).writerow([time_since_start, get_datetime(current_time), str(temperature)])
    return time_since_start
