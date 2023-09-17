import pathlib
from typing import TypedDict
from hegre_downloader.hegre import Hegre

import os
import re
import json
import argparse
import requests
from requests.cookies import RequestsCookieJar
from datetime import datetime, timezone
from base64 import b64encode, b64decode
from urllib.parse import urlparse
from rich.console import Console


class CapturedWebsite(TypedDict):
    url: str
    timestamp: str
    cookies: dict[str, str]
    encoded_content: str


def capture_website(url: str, cookies: dict[str, str] = {}) -> str:
    """Captures the website with the given URL and cookies and writes it into a file with some meta information

    Args:
        url (str): URL to capture
        cookies (dict[str, str], optional): Cookies that should be used for the request. Defaults to {}.

    Raises:
        requests.HTTPError: If the request failed (e.g. a non 2xx status code)

    Returns:
        str: Name of the file that was written
    """
    timestamp = datetime.now(timezone.utc)
    date_str = timestamp.strftime("%Y.%m.%d.%H.%M.%S")

    info_dict: CapturedWebsite = {
        "url": url,
        "timestamp": timestamp.isoformat(),
        "cookies": cookies,
    }

    response = requests.get(url, cookies=cookies)
    response.raise_for_status()

    info_dict["encoded_content"] = b64encode(response.content).decode("utf-8")

    filename = f"{date_str}_{url_to_filename(url)}.json"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(info_dict))
        console.print(f"Capture of {url} was written to '{filename}'")

        return filename


def read_captured_website(filename: str) -> str:
    """Read a captured website file and return the decoded content

    Args:
        filename (str): File to read

    Returns:
        str: Decoded content
    """
    with open(filename, "r", encoding="utf-8") as file:
        parsed_contents: CapturedWebsite = json.loads(file.read())

        return b64decode(parsed_contents["encoded_content"]).decode("utf-8")


def url_to_filename(url: str) -> str:
    """Convert an URL into a filename compatible version

    Args:
        url (str): the URL to convert

    Returns:
        str: filename compatible version of the URL
    """
    parsed_url = urlparse(url)

    # remove www host from hostname, if present
    sanitised_url = parsed_url.hostname.replace("www.", "")
    sanitised_url += parsed_url.path

    # remove any characters that are not allowed in filenames
    return re.sub("[^a-zA-Z0-9_]", "_", sanitised_url)


def sanitise_cookie_jar(
    cookies: RequestsCookieJar,
    sensitive_cookies: list[str] = ["login", "_www.hegre.com_session"],
    redacted_str: str = "REDACTED",
) -> dict[str, str]:
    """Converts a requests.cookies.RequestCookieJar into a dictionary and redacts sensitive cookies by replacing their values

    Args:
        cookies (RequestsCookieJar): Cookie jar to sanitise
        sensitive_cookies (list[str], optional): Name of the cookies that should be redacted. Defaults to ["login", "_www.hegre.com_session"].
        redacted_str (str, optional): Value with which the sensitive cookie values should be redacted (i.e. replaced) with. Defaults to "REDACTED".

    Returns:
        dict[str, str]: Cookie jar as dictionary with the sensitive keys redacted
    """
    cookie_dict = cookies.get_dict()

    for sensitive_cookie in sensitive_cookies:
        if sensitive_cookie in cookie_dict:
            cookie_dict[sensitive_cookie] = redacted_str

    return cookie_dict


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="capture_website",
        description="Capture a website in a machine-readable format, including metadata on how the website was fetched",
    )
    parser.add_argument(
        "urls",
        metavar="URL",
        nargs="*",
        help="Hegre URL(s) to download",
        action="store",
    )
    parser.add_argument(
        "-r",
        metavar="FILE",
        action="store",
        type=pathlib.Path,
        help="Read a capture file and print the website content",
    )
    args = parser.parse_args()

    console = Console()

    if args.r:
        print(read_captured_website(args.r))
    else:
        username = os.environ.get("username")
        password = os.environ.get("password")

        hegre = Hegre()
        if not username or not password:
            console.print("No credentials provided")
            cookies = hegre._cookies
        else:
            console.print(f"Credentials provided, logging in")
            hegre.login(username, password)
            cookies = sanitise_cookie_jar(hegre._session.cookies)

        for url in args.urls:
            try:
                file = capture_website(url, cookies)
            except requests.HTTPError as e:
                console.print(f"An error occured while capturing {url}: {e}")
