import math
import re

from typing import Optional
from urllib.parse import urlsplit, urlunsplit


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


def strip_query(url: str) -> str:
    """Removes query string and fragment from a URL

    Args:
        url (str): URL, e.g. "https://host/file.mp4?v=123"

    Returns:
        str: URL without parameters, e.g. "https://host/file.mp4"
    """
    parts = urlsplit(url.strip())
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


def extract_css_url(style: Optional[str]) -> Optional[str]:
    """Extracts the (parameterless) URL of a CSS `url(...)` expression

    Args:
        style (Optional[str]): Inline style, e.g. "background-image: url('https://...')"

    Returns:
        Optional[str]: URL without parameters or None if no URL was found
    """
    if style and (match := re.search(r"url\(\s*['\"]?(https?://[^'\")\s]+)", style)):
        return strip_query(match.group(1))

    return None
