import time

FORMAT_SPECIFIER = "%d %B %Y %I:%M:%S %p"


def get_datetime(time_since_epoch: float | None = None) -> str:
    """
    Converts a float (as returned by **time.time()**) to a string in
    Day Month Year Hours:Minutes:Seconds AM/PM format. If **time_since_epoch** is **None**, use the
    current time instead.
    """
    return time.strftime(FORMAT_SPECIFIER, time.localtime(time_since_epoch))


def get_file_friendly_datatime(time_since_epoch: float | None = None) -> str:
    """
    Calls `get_datetime()` and replaces colons (:) with a unicode character that looks like a colon.
    """
    return get_datetime(time_since_epoch).replace(":", "ː")
