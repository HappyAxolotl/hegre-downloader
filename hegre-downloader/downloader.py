import os
import re
import sys
import argparse
import pathlib

from hegre import Hegre
from sort_option import SortOption
from exceptions import HegreError
from configuration import Configuration

from dotenv import load_dotenv
from rich.progress import Progress, TaskID
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor

DOWNLOAD_TASK_PREFIX = "[{:>4} / {:>4}] "


def load_config_from_args() -> Configuration:
    parser = argparse.ArgumentParser(
        prog="downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Downloader and metadata extractor for hegre.com

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
        default=["https://www.hegre.com/movies"],
    )
    parser.add_argument(
        "-d",
        metavar="PATH",
        help="Destination folder",
        action="store",
        required=True,
        type=pathlib.Path,
    )
    parser.add_argument(
        "-r",
        metavar="HEIGHT_IN_PX",
        help="Preferred resolution for movies (height in pixels, e.g. 480, 2160). If this argument is omitted or the requested resolution is not available, the highest available resolution is selcetd.",
        type=int,
        action="store",
    )
    parser.add_argument(
        "-p",
        help="Number of parallel tasks. Defaults to 1.",
        type=int,
        action="store",
        default=1,
    )
    parser.add_argument(
        "--sort",
        help="Sorting when downloading all movies/galleries. Defaults to 'most_recent'. Valid values are 'most_recent', 'most_viewed', 'top_rated'.",
        action="store",
        default=SortOption.MOST_RECENT,
    )
    parser.add_argument(
        "--retries",
        help="Number of retries for failed downloads. Defaults to 2. Set to 0 to disable retries.",
        type=int,
        action="store",
        default=2,
    )
    parser.add_argument(
        "--no-thumb",
        help="Do not download thumbnails",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--no-meta",
        help="Do not create metadata file",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--no-subtitles",
        help="Do not download subtitles",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--no-download",
        help="Do not download the actual file (movie or gallery)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--subtitles",
        help="Language(s) of subtitles that should be downloaded. Will only download available languages. Defaults to 'english'. Multiple langauges must separated by comma (e.g. 'english,german,japanese').",
        action="store",
        default="english",
    )
    parser.add_argument(
        "--screengrabs", help="Download screengrabs", action="store_true", default=False
    )
    parser.add_argument(
        "--trailer", help="Download trailer", action="store_true", default=False
    )

    args = parser.parse_args()

    if args.no_thumb and args.no_meta and args.no_subtitles and args.no_download:
        console.print(
            "[red]By specifying --no-thumb, --no-meta, --no-subtitles and --no-download you've essentially told the tool to do nothing. Please use a maximum of three of these options."
        )
        sys.exit(1)

    subtitles = args.subtitles.split(",")
    subtitles = [language.lower() for language in subtitles]

    return Configuration(
        args.urls,
        args.d,
        args.retries,
        args.p,
        args.sort,
        no_thumb=args.no_thumb,
        no_meta=args.no_meta,
        no_subtitles=args.no_subtitles,
        no_download=args.no_download,
        screengrabs=args.screengrabs,
        trailer=args.trailer,
        resolution=args.r,
        subtitles=subtitles,
    )


def login() -> None:
    try:
        with console.status("Logging in"):
            hegre.login(username, password)

        console.print("[green]:heavy_check_mark: Login successful[/]")
    except HegreError as e:
        console.print(f"[red]:x: {e}")
        sys.exit(1)


def download_urls(urls: list[str], configuration: Configuration) -> None:
    if not urls:
        return

    with Progress() as progress:
        with ThreadPoolExecutor(max_workers=configuration.parallel_tasks) as pool:
            for count, url in enumerate(urls):
                try:
                    pool.submit(
                        download_url,
                        url,
                        configuration,
                        DOWNLOAD_TASK_PREFIX.format(count + 1, len(urls)),
                        progress,
                    )
                except HegreError as e:
                    progress.console.print(f"[red] {e}")


def download_url(
    url: str, configuration: Configuration, task_prefix: str, progress: Progress
) -> None:
    # Movie
    if re.match(r"^https?:\/\/www\.hegre\.com\/(films|massage|sexed)\/", url):
        movie = hegre.get_movie_from_url(url)
        hegre.download_movie(
            movie, configuration, progress=progress, task_prefix=task_prefix
        )
    # TODO: Gallery
    # ^https?:\/\/www\.hegre\.com\/photos\/
    else:
        raise HegreError(f"Unsupported URL: {url}!")


if __name__ == "__main__":
    load_dotenv()
    console = Console()

    configuration = load_config_from_args()

    username = os.environ.get("username")
    password = os.environ.get("password")

    if not username or not password:
        console.print("[red]Please provide username and password!")
        sys.exit(1)

    hegre = Hegre()
    login()

    for url in configuration.urls:
        console.print(f"Downloading {url}:")
        try:
            urls = hegre.resolve_urls(url, sort=configuration.sort, show_progress=True)
            download_urls(urls, configuration)
        except HegreError as e:
            console.print(f"[red]:x: {e}")
