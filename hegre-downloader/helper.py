import json
import math

from datetime import date
from typing import Any

from movie import ObjectType


class HegreJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, ObjectType):
            return str(o)

        return o.__dict__


def duration_to_seconds(duration: str, delimiter: str = ":") -> int:
    """Converts a duration string into seconds

    Args:
        duration (str): Duration string in the form of "hh:mm:ss", "mm:ss" or "ss"

    Raises:
        ValueError: If the duration string is in an invalid format

    Returns:
        int: Number of seconds
    """
    elements = duration.split(delimiter)

    match len(elements):
        case 3:
            return int(elements[0]) * 3600 + int(elements[1]) * 60 + int(elements[2])
        case 2:
            return int(elements[0]) * 60 + int(elements[1])
        case 1:
            return int(elements[0])
        case _:
            raise ValueError("Could not parse duration string into seconds")


def convert_size(size_bytes: int) -> str:
    """Convert a file size in byte into a human readable string
    see: https://stackoverflow.com/a/14822210

    Args:
        size_bytes (int): Number of bytes

    Returns:
        str: Number of bytes as human readable string
    """
    if size_bytes == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)

    return "%s %s" % (s, size_name[i])
