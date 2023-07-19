import json

from datetime import date
from typing import Any

from movie import MovieType


class HegreJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, MovieType):
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
