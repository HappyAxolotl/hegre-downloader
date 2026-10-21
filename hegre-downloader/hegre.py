from __future__ import annotations

import os
import re
import json
import httpx


from bs4 import BeautifulSoup
from rich.progress import Progress, TaskID
from urllib.parse import urlparse
from httpx import HTTPError, StreamError
from pathlib import Path
from typing import Optional

from model.movie import HegreMovie
from model.gallery import HegreGallery
from model.hegre_object import HegreObject
from sort_option import SortOption
from exceptions import HegreError, MovieAlreadyDownloaded
from configuration import Configuration

PARSER = "html.parser"
MOVIE_PROGRESS = "[green] [{:>4} / {:>4}] Fetching movie URLs"
GALLERY_PROGRESS = "[green] [{:>4} / {:>4}] Fetching gallery URLs"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
)
# generous read timeout, the CDN can be slow to deliver large files
TIMEOUT = httpx.Timeout(60.0, connect=15.0)
MAX_LISTING_PAGES = 1000  # safety net against endless pagination loops


class Hegre:
    _session: httpx.Client
    _logged_in: bool

    def __init__(
        self, locale: str = "en", country: str = "US", width: int = 3840
    ) -> None:
        self._session = httpx.Client(
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=TIMEOUT,
        )
        self._logged_in = False

        cookies = {"locale": locale, "country": country, "_width": str(width)}
        for k, v in cookies.items():
            self._session.cookies.set(k, v, domain="www.hegre.com")

    def close(self) -> None:
        self._session.close()

    def login(self, username: str, password: str) -> None:
        """Starts a session with the given credentials

        Args:
            username (str): Hegre username
            password (str): Hegre password

        Raises:
            HegreError: If the authenticity_token could not be extracted or the login failed
        """
        login_page = self._get_page("https://www.hegre.com/login")
        token_input = login_page.select_one('input[name="authenticity_token"]')

        if not token_input:
            raise HegreError("Could not extract authenticity_token from login page!")

        data = {
            "authenticity_token": token_input.attrs["value"],
            "username": username,
            "password": password,
        }

        r = self._session.post(
            "https://www.hegre.com/login",
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.hegre.com/login",
            },
        )

        if r.status_code != 200:
            raise HegreError(f"Failed to login (HTTP {r.status_code}): {r.text[:200]}")

        try:
            login = json.loads(r.text)
        except json.JSONDecodeError:
            raise HegreError(
                f"Failed to login, unexpected response (the login flow may have changed): {r.text[:200]}"
            )

        if login.get("status") != "success":
            raise HegreError(f"Failed to login: {login.get('message') or r.text[:200]}")

        self._logged_in = True

    def resolve_urls(
        self,
        url: str,
        sort: SortOption = SortOption.MOST_RECENT,
        show_progress: Optional[bool] = False,
    ) -> list[str]:
        # hegre.com/films has no listing page (404), treat it like hegre.com/movies
        if re.match(r"^https?:\/\/www\.hegre\.com\/(movies|films)\/?$", url):
            total = self.get_total_movie_count()
            urls = []

            if show_progress:
                with Progress() as progress:
                    task_id = progress.add_task(
                        MOVIE_PROGRESS.format(0, total), total=total
                    )
                    urls = self.get_movie_urls(
                        total, sort, progress=progress, task_id=task_id
                    )
            else:
                urls = self.get_movie_urls(total, sort)

            return urls
        elif re.match(r"^https?:\/\/www\.hegre\.com\/photos\/?$", url):
            total = self.get_total_gallery_count()
            urls = []

            if show_progress:
                with Progress() as progress:
                    task_id = progress.add_task(
                        GALLERY_PROGRESS.format(0, total), total=total
                    )
                    urls = self.get_gallery_urls(
                        total, sort, progress=progress, task_id=task_id
                    )
            else:
                urls = self.get_gallery_urls(total, sort)

            return urls
        elif re.match(r"^https?:\/\/www\.hegre\.com\/models\/[a-z0-9-]+\/?$", url):
            return self.get_model_urls(url)
        elif re.match(
            r"^https?:\/\/www\.hegre\.com\/(photos|films|massage|sexed|orgasms)\/[^\/?#]+",
            url,
        ):
            return [url]
        else:
            raise HegreError(
                "Unsupported URL! Only galleries, movies, films, massage, sexed and orgasms are supported."
            )

    def get_model_urls(self, url: str) -> list[str]:
        model_page = self._get_page(url)

        return _item_urls(model_page, "#galleries-listing .item") + _item_urls(
            model_page, "#films-listing .item"
        )

    def get_movie_urls(
        self,
        total: int,
        sort: SortOption,
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None,
    ) -> list[str]:
        return self._get_listing_urls(
            "https://www.hegre.com/movies?films_sort={sort}&films_page={page}",
            "#films-listing .item",
            MOVIE_PROGRESS,
            total,
            sort,
            progress,
            task_id,
        )

    def get_gallery_urls(
        self,
        total: int,
        sort: SortOption,
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None,
    ) -> list[str]:
        return self._get_listing_urls(
            "https://www.hegre.com/photos?galleries_sort={sort}&galleries_page={page}",
            "#galleries-listing .item",
            GALLERY_PROGRESS,
            total,
            sort,
            progress,
            task_id,
        )

    def _get_listing_urls(
        self,
        url_template: str,
        item_selector: str,
        progress_template: str,
        total: int,
        sort: SortOption,
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None,
    ) -> list[str]:
        urls = []

        for page in range(1, MAX_LISTING_PAGES + 1):
            listing_page = self._get_page(url_template.format(sort=sort, page=page))
            urls_on_page = _item_urls(listing_page, item_selector)

            # the last page shows a ".hint" ("This list is currently empty.")
            if not urls_on_page:
                break

            urls.extend(urls_on_page)

            if progress is not None and task_id is not None:
                progress.update(
                    task_id,
                    advance=len(urls_on_page),
                    description=progress_template.format(len(urls), total),
                )

        return urls

    def get_total_movie_count(self) -> int:
        return self._get_total_count("https://www.hegre.com/movies?films_page=1")

    def get_total_gallery_count(self) -> int:
        return self._get_total_count("https://www.hegre.com/photos?galleries_page=1")

    def _get_total_count(self, url: str) -> int:
        count = self._get_page(url).select_one("h2 strong")

        if count and (match := re.search(r"\d+", count.text.replace(",", ""))):
            return int(match.group(0))

        return 0  # only used for progress display

    def get_movie_from_url(self, url: str) -> HegreMovie:
        return HegreMovie.from_film_page(url, self._get_page(url))

    def get_gallery_from_url(self, url: str) -> HegreGallery:
        return HegreGallery.from_gallery_page(url, self._get_page(url))

    def download_movie(
        self,
        movie: HegreMovie,
        configuration: Configuration,
        progress: Optional[Progress] = None,
        task_prefix: str = "",
    ) -> None:
        # trailers are public and can be downloaded without an account
        if not configuration.trailers_only:
            self._ensure_logged_in()

        if not movie.downloads and not configuration.no_download:
            raise HegreError(f"No download links found for '{movie.title}'")

        if movie.has_only_trailers() and not configuration.no_download:
            raise HegreError(
                f"Only the trailer of '{movie.title}' is available. Is your subscription still active?"
            )

        dest_folder = _destination_folder(movie, configuration)

        try:
            url = None
            if movie.downloads:
                _, url = _select_resolution(movie, configuration, progress, task_prefix)

            if not configuration.no_download:
                filename, _ = generate_filename(url, movie)

                self._download_with_retries(
                    url,
                    dest_folder,
                    filename,
                    progress,
                    task_prefix,
                    max_attempts=configuration.retries + 1,
                )

            self._download_extras(movie, dest_folder, configuration, url)

            if not configuration.no_subtitles:
                subtitle_urls = movie.get_subtitle_download_urls(
                    configuration.subtitles
                )
                for url in subtitle_urls:
                    sub_filename, _ = generate_filename(url, movie)
                    self._download_file(url, os.path.join(dest_folder, sub_filename))

            if configuration.screengrabs and movie.screengrabs_url:
                screengrab_file, _ = generate_filename(movie.screengrabs_url, movie)
                self._download_file(
                    movie.screengrabs_url, os.path.join(dest_folder, screengrab_file)
                )

            if configuration.trailer and movie.trailers:
                if configuration.resolution in movie.trailers:
                    _, url = movie.get_trailer_download_url_for_res(
                        configuration.resolution
                    )
                else:
                    _, url = movie.get_highest_res_trailer_download_url()
                trailer_file, _ = generate_filename(url, movie)
                self._download_with_retries(
                    url,
                    dest_folder,
                    trailer_file,
                    progress,
                    task_prefix,
                    max_attempts=configuration.retries + 1,
                )
            elif configuration.trailers_only:
                raise HegreError(f"No trailer found for '{movie.title}'")

        except MovieAlreadyDownloaded as e:
            if progress:
                progress.console.print(f"{task_prefix}Skipping '{movie.title}': {e}")
            else:
                raise e

    def download_gallery(
        self,
        gallery: HegreGallery,
        configuration: Configuration,
        progress: Optional[Progress] = None,
        task_prefix: str = "",
    ) -> None:
        self._ensure_logged_in()

        if not gallery.downloads and not configuration.no_download:
            raise HegreError(f"No download links found for '{gallery.title}'")

        dest_folder = _destination_folder(gallery, configuration)

        try:
            url = None
            if gallery.downloads:
                _, url = _select_resolution(
                    gallery, configuration, progress, task_prefix
                )

            if not configuration.no_download:
                filename, _ = generate_filename(url, gallery)

                self._download_with_retries(
                    url,
                    dest_folder,
                    filename,
                    progress,
                    task_prefix,
                    max_attempts=configuration.retries + 1,
                )

            self._download_extras(gallery, dest_folder, configuration, url)
        except MovieAlreadyDownloaded as e:
            if progress:
                progress.console.print(f"{task_prefix}Skipping '{gallery.title}': {e}")
            else:
                raise e

    def _download_extras(
        self,
        hegre_object: HegreObject,
        dest_folder: str,
        configuration: Configuration,
        download_url: Optional[str],
    ) -> None:
        """Writes the metadata file and downloads the thumbnail"""
        # the metadata file is named after the movie/gallery file
        name_source = download_url or hegre_object.cover_url or hegre_object.url

        if not configuration.no_meta:
            _, metadata_filename = generate_filename(name_source, hegre_object)
            hegre_object.write_metadata_file(dest_folder, metadata_filename)

        if not configuration.no_thumb and hegre_object.cover_url:
            thumbnail, _ = generate_filename(hegre_object.cover_url, hegre_object)
            thumbnail_file = os.path.join(dest_folder, thumbnail)
            if not os.path.exists(thumbnail_file):
                self._download_file(hegre_object.cover_url, thumbnail_file)

    def _download_with_retries(
        self,
        url: str,
        destination_folder: Path,
        filename: str,
        progress: Optional[Progress] = None,
        task_prefix: str = "",
        max_attempts: int = 3,
    ):
        dest_file = os.path.join(destination_folder, filename)
        temp_file = os.path.join(destination_folder, f"{filename}.temp")

        if os.path.exists(dest_file):
            raise MovieAlreadyDownloaded(f"{filename} exists already!")

        for attempt in range(1, max_attempts + 1):
            task_id = None
            if progress:
                task_id = progress.add_task(task_prefix + filename, start=False)

            try:
                self._download_file(url, temp_file, progress, task_id)
                break
            except (HTTPError, StreamError) as e:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

                if progress and task_id is not None:
                    progress.update(
                        task_id, description=f"[red strike]{task_prefix}{filename}[/]"
                    )
                    progress.stop_task(task_id)

                if attempt >= max_attempts:
                    raise HegreError(
                        f"Failed to download '{filename}' after {attempt} attempt(s): {e}"
                    ) from e
                elif progress:
                    progress.console.print(
                        f"[yellow]:warning: Failed attempt {attempt} to download '{filename}': {e}"
                    )

        # we can assume a successful download here
        os.replace(temp_file, dest_file)

    def _download_file(
        self,
        url: str,
        dest_file: str,
        progress: Optional[Progress] = None,
        task_id: Optional[TaskID] = None,
        chunk_size: int = 1024 * 1024,
    ):
        with self._session.stream("GET", url) as stream:
            stream.raise_for_status()

            with open(dest_file, "wb") as file:
                content_length = stream.headers.get("Content-Length")

                if progress and task_id is not None:
                    progress.update(
                        task_id, total=int(content_length) if content_length else None
                    )
                    progress.start_task(task_id)

                for chunk in stream.iter_bytes(chunk_size=chunk_size):
                    file.write(chunk)
                    if progress and task_id is not None:
                        progress.update(task_id, advance=len(chunk))

    def _get_page(self, url: str) -> BeautifulSoup:
        try:
            response = self._session.get(url)
            response.raise_for_status()
        except HTTPError as e:
            raise HegreError(f"Failed to load {url}: {e}") from e

        return BeautifulSoup(response.text, PARSER)

    def _ensure_logged_in(self) -> None:
        if not self._logged_in:
            raise HegreError("No active session detected, please login first!")


def _item_urls(page: BeautifulSoup, item_selector: str) -> list[str]:
    urls = []

    for item in page.select(item_selector):
        if link := item.select_one("a[href]"):
            urls.append("https://www.hegre.com" + link.attrs["href"])

    return urls


def _destination_folder(hegre_object: HegreObject, configuration: Configuration) -> str:
    # create subfolder for each year, if the movie/gallery has a date
    if hegre_object.date:
        dest_folder = os.path.join(
            configuration.destination_folder, str(hegre_object.date.year)
        )
    else:
        dest_folder = str(configuration.destination_folder)

    os.makedirs(dest_folder, exist_ok=True)

    return dest_folder


def _select_resolution(
    hegre_object: HegreObject,
    configuration: Configuration,
    progress: Optional[Progress],
    task_prefix: str,
) -> tuple[int, str]:
    """Returns the preferred resolution or the highest one if it is not available"""
    try:
        return hegre_object.get_download_url_for_res(configuration.resolution)
    except KeyError as e:
        if progress:
            progress.console.print(
                f"[yellow]{task_prefix}{e} Using the highest resolution instead."
            )
        return hegre_object.get_highest_res_download_url()


def generate_filename(url: str, hegre_object: HegreObject) -> tuple[str, str]:
    original_name = os.path.basename(urlparse(url).path)
    name, _ = os.path.splitext(original_name)

    if hegre_object.date:
        date_str = hegre_object.date.strftime("%Y.%m.%d")

        return (
            f"{date_str}-{hegre_object.code}-{original_name}",
            f"{date_str}-{hegre_object.code}-{name}.json",
        )
    else:
        return (
            f"{hegre_object.code}-{original_name}",
            f"{hegre_object.code}-{name}.json",
        )
