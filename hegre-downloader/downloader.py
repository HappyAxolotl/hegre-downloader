import os
import re
import sys
import argparse
import pathlib

from hegre import Hegre
from exceptions import HegreError

from dotenv import load_dotenv
from rich.progress import Progress, TaskID
from rich.console import Console

DOWNLOAD_TASK_PREFIX = "[{:>4} / {:>4}] "


def login() -> None:
    try:
        with console.status("Logging in"):
            hegre.login(username, password)

        console.print("[green]:heavy_check_mark: Login successful[/]")
    except HegreError as e:
        console.print(f"[red]:x: {e}")
        sys.exit(1)


def download_urls(urls: list[str], destination_folder: str) -> None:
    if not urls:
        return

    with Progress() as progress:
        for count, url in enumerate(urls):
            try:
                download_url(
                    url,
                    destination_folder,
                    DOWNLOAD_TASK_PREFIX.format(count + 1, len(urls)),
                    progress,
                )
            except HegreError as e:
                progress.console.print(f"[red] {e}")


def download_url(
    url: str, destination_folder: str, task_prefix: str, progress: Progress
) -> None:
    # Movie
    if re.match(r"^https?:\/\/www\.hegre\.com\/(films|massage|sexed)\/", url):
        movie = hegre.get_movie_from_url(url)
        hegre.download_movie(
            movie, destination_folder, progress=progress, task_prefix=task_prefix
        )
    # TODO: Gallery
    # ^https?:\/\/www\.hegre\.com\/photos\/
    else:
        raise HegreError(f"Unsupported URL: {url}!")


if __name__ == "__main__":
    load_dotenv()
    console = Console()

    parser = argparse.ArgumentParser(
        prog="hegre-downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Downloader for hegre.com

You can specify one or more URLs that will be downloaded. If you do not provide a URL, it will download all movies. The following URLs are supported:
- All movies:
    https://www.hegre.com/movies
- Single movie of type film:
    https://www.hegre.com/films/title-of-the-film
    https://www.hegre.com/films/69
- Single movie of type massage:
    https://www.hegre.com/massage/title-of-the-massage-film
    https://www.hegre.com/massage/69
- Single movie of type sexed:
    https://www.hegre.com/sexed/title-of-the-sexed-film
    https://www.hegre.com/sexed/69
""",
    )
    parser.add_argument(
        "urls",
        metavar="URL",
        nargs="*",
        help="Hegre URL(s) to download. If none is specified, defaults to https://www.hegre.com/movies",
    )
    parser.add_argument(
        "-d",
        "--destination",
        help="Destination folder",
        action="store",
        required=True,
        type=pathlib.Path,
    )
    args = parser.parse_args()

    username = os.environ.get("username")
    password = os.environ.get("password")

    if not username or not password:
        console.print("[red]Please provide username and password!")
        sys.exit(1)

    hegre = Hegre()
    login()

    # if no URLs are provided, fallback to downloading all movies
    if len(args.urls) == 0:
        args.urls.append("https://www.hegre.com/movies")

    for url in args.urls:
        console.print(f"Downloading {url}:")
        try:
            with Progress() as progress:
                urls = hegre.resolve_urls(url, progress=progress)

            download_urls(urls, args.destination)
        except HegreError as e:
            console.print(f"[red]:x: {e}")
