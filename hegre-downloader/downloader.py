import os
import re
import sys
import argparse
import pathlib

from hegre import Hegre
from model.movie import HegreMovie
from model.gallery import HegreGallery
from sort_option import SortOption
from exceptions import HegreError
from configuration import Configuration

from dotenv import load_dotenv
from rich.progress import Progress
from rich.console import Console
from concurrent.futures import ThreadPoolExecutor

DOWNLOAD_TASK_PREFIX = "[{:>4} / {:>4}] "
archive: set[str] = set()


def load_config_from_args() -> Configuration:
    parser = argparse.ArgumentParser(
        prog="downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""Downloader and metadata extractor for hegre.com

You can specify one or more URLs that will be downloaded. The following URLs are supported:
- Single movie:
    https://www.hegre.com/films/title-of-the-film
    https://www.hegre.com/massage/title-of-the-massage-film
    https://www.hegre.com/sexed/title-of-the-sexed-film
- All movies:
    https://www.hegre.com/movies
- Single gallery:
    https://www.hegre.com/photos/title-of-the-gallery
- All galleries:
    https://www.hegre.com/photos
- All movies and galleries of a model:
    https://www.hegre.com/models/name-of-model
""",
    )
    parser.add_argument(
        "urls",
        metavar="URL",
        nargs="+",
        help="Hegre URL(s) to download",
        action="store",
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
        metavar="NUM_OF_TASKS",
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
    parser.add_argument(
        "--download-archive",
        metavar="FILE",
        action="store",
        type=pathlib.Path,
        dest="download_archive",
        help="Download only videos/galleries not listed in the archive file. Record the IDs of all downloaded videos/galleries in it",
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
        download_archive=args.download_archive,
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
        if configuration.parallel_tasks > 1:
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
                        progress.console.print(f"[red] Error downloading {url}: {e}")
        else:
            for count, url in enumerate(urls):
                download_url(
                    url,
                    configuration,
                    DOWNLOAD_TASK_PREFIX.format(count + 1, len(urls)),
                    progress,
                )


def download_url(
    url: str, configuration: Configuration, task_prefix: str, progress: Progress
) -> None:
    if re.match(r"^https?:\/\/www\.hegre\.com\/(films|massage|sexed|orgasms)\/", url):
        movie = hegre.get_movie_from_url(url)
        if movie.archive_id() in archive:
            console.print(
                f"Movie '{movie.title}' [{movie.code}] has already been recorded in the archive"
            )
        else:
            hegre.download_movie(
                movie, configuration, progress=progress, task_prefix=task_prefix
            )
            record_download_archive(configuration, movie)
    elif re.match(r"^https?:\/\/www\.hegre\.com\/photos\/", url):
        gallery = hegre.get_gallery_from_url(url)
        if gallery.archive_id() in archive:
            console.print(
                f"Gallery '{gallery.title}' [{gallery.code}] has already been recorded in the archive"
            )
        else:
            hegre.download_gallery(
                gallery, configuration, progress=progress, task_prefix=task_prefix
            )
            record_download_archive(configuration, gallery)
    else:
        raise HegreError(f"Unsupported URL: {url}!")


def load_download_archive(filename: str) -> None:
    """Load download archive from file, if a filename is specified"""
    if not filename or not os.path.exists(filename):
        return

    try:
        with open(filename, "r", encoding="utf-8") as archive_file:
            for line in archive_file:
                archive.add(line.strip())
    except OSError:
        raise


def record_download_archive(
    configuration: Configuration,
    hegre_object: HegreMovie | HegreGallery,
) -> None:
    if configuration.download_archive is None:
        return

    id = hegre_object.archive_id()

    with open(configuration.download_archive, "a", encoding="utf-8") as archive_file:
        archive_file.write(id + "\n")

    archive.add(id)


if __name__ == "__main__":
    load_dotenv()
    console = Console()

    configuration = load_config_from_args()
    load_download_archive(configuration.download_archive)

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
