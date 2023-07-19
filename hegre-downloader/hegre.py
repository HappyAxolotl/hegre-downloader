from __future__ import annotations

import os
import re
import json
import requests


from bs4 import BeautifulSoup
from rich.progress import Progress, TaskID
from enum import Enum
from urllib.parse import urlparse
from requests import HTTPError
from requests.exceptions import ChunkedEncodingError

from movie import HegreMovie
from exceptions import HegreError, MovieAlreadyDownloaded


PARSER = "html.parser"
MOVIE_PROGRESS = "[green] [{:>4} / {:>4}] Fetching movie URLs"


class SortOptions(Enum):
    MOST_RECENT = "most_recent"
    MOST_VIEWED = "most_viewed"
    TOP_RATED = "top_rated"

    def __str__(self) -> str:
        return self.value


class Hegre:
    _session: requests.Session
    _cookies: dict[str, str]

    def __init__(
        self, locale: str = "en", country: str = "US", width: int = 3840
    ) -> None:
        self._session = requests.Session()
        self._cookies = {"locale": locale, "country": country, "_width": str(width)}

        for k, v in self._cookies.items():
            self._session.cookies.set(k, v)

    def login(self, username: str, password: str) -> None:
        """Starts a session with the given credentials

        Args:
            username (str): Hegre username
            password (str): Hegre password

        Raises:
            HegreError: If the authenticity_token could not be extracted or the login failed
        """
        raw_login_page = self._session.get("https://www.hegre.com/login")
        login_page = BeautifulSoup(raw_login_page.text, PARSER)
        find_token = login_page.select('input[name="authenticity_token"]')

        if token_input := find_token[0]:
            token = token_input.attrs["value"]

            data = {
                "authenticity_token": token,
                "username": username,
                "password": password,
            }

            r = self._session.post(
                "https://www.hegre.com/login",
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                    "X-Requested-With": "XMLHttpRequest",
                },
            )

            if r.status_code != 200:
                raise HegreError(f"Failed to login (HTTP {r.status_code}): {r.text}")

            login = json.loads(r.text)
            if "status" not in login or login["status"] != "success":
                raise HegreError(f"Failed to login (HTTP {r.status_code}): {r.text}")
        else:
            raise HegreError("Could not extract authenticity_token from login page!")

    def resolve_urls(
        self,
        url: str,
        sort: SortOptions = SortOptions.MOST_RECENT,
        progress: Progress = None,
    ) -> list[str]:
        if re.match(r"^https?:\/\/www\.hegre\.com\/movies", url):
            total = self.get_total_movie_count()
            if progress:
                task_id = progress.add_task(
                    MOVIE_PROGRESS.format(0, total), total=total
                )
            return self.get_movie_urls(total, sort, progress, task_id)
        elif re.match(r"^https?:\/\/www\.hegre\.com\/(films|massage|sexed)\/", url):
            return [url]
        else:
            raise HegreError(
                "Unsupported URL! Only movies, films, massage and sexed are supported at the moment."
            )

    def get_movie_urls(
        self,
        total: int,
        sort: SortOptions,
        progress: Progress = None,
        task_id: TaskID = None,
    ) -> list[str]:
        urls = []
        page = 1

        while True:
            movies_page_res = requests.get(
                f"https://www.hegre.com/movies?films_sort={str(sort)}&films_page={page}",
                cookies=self._cookies,
            )
            movies_page = BeautifulSoup(movies_page_res.text, PARSER)

            if len(movies_page.select(".hint")) < 1:
                urls_on_page = []
                for item in movies_page.select("#films-listing .item"):
                    url = "https://www.hegre.com" + item.select_one("a").attrs["href"]
                    urls_on_page.append(url)

                urls.extend(urls_on_page)

                if progress != None and task_id != None:
                    progress.update(
                        task_id,
                        advance=len(urls_on_page),
                        description=MOVIE_PROGRESS.format(len(urls), total),
                    )

                page += 1
            else:
                break

        return urls

    def get_total_movie_count(self, sort: SortOptions = SortOptions.MOST_RECENT) -> int:
        movies_page_res = requests.get(
            f"https://www.hegre.com/movies?films_sort={str(sort)}&films_page=1",
            cookies=self._cookies,
        )

        movies_page = BeautifulSoup(movies_page_res.text, PARSER)
        return int(movies_page.select_one("h2 strong").text)

    def get_movie_from_url(self, url: str) -> HegreMovie:
        if "login" not in self._session.cookies:
            raise HegreError("No active session detected, please login first!")

        film_page_res = self._session.get(url)
        film_page = BeautifulSoup(film_page_res.text, PARSER)

        return HegreMovie.from_film_page(url, film_page)

    def download_movie(
        self,
        movie: HegreMovie,
        destination_folder: str,
        res: int | None = None,
        progress: Progress | None = None,
        task_prefix: str | None = None,
    ) -> None:
        if "login" not in self._session.cookies:
            raise HegreError("No active session detected, please login first!")

        # create subfolder for each year, if the movie has a date
        if movie.date:
            destination_folder = os.path.join(destination_folder, str(movie.date.year))

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder, exist_ok=True)

        res, url = movie.get_download_url_for_res(res)

        filename, metadata_filename = generate_movie_filename(url, movie)
        thumbnail, _ = generate_movie_filename(movie.cover_url, movie)

        try:
            self._download_with_retries(
                url, destination_folder, filename, progress, task_prefix
            )
            movie.write_metadata_file(destination_folder, metadata_filename)
            self._download_file(
                movie.cover_url, os.path.join(destination_folder, thumbnail)
            )
        except MovieAlreadyDownloaded as e:
            if progress:
                progress.console.print(f"{task_prefix}Skipping '{movie.title}': {e}")
            else:
                raise e

    def _download_with_retries(
        self,
        url: str,
        destination_folder: str,
        filename: str,
        progress: Progress = None,
        task_prefix: str | None = None,
        max_retries: int = 3,
    ):
        dest_file = os.path.join(destination_folder, filename)
        temp_file = os.path.join(destination_folder, f"{filename}.temp")

        if os.path.exists(dest_file):
            raise MovieAlreadyDownloaded(f"{filename} exists already!")

        if progress:
            task_id = progress.add_task(task_prefix + filename, start=False)

        attempt = 1
        failed = True
        while failed and attempt <= max_retries:
            try:
                self._download_file(url, temp_file, progress, task_id)
                failed = False
            except (HTTPError, ChunkedEncodingError) as e:
                os.remove(temp_file)

                if attempt + 1 > max_retries:
                    raise e
                elif progress:
                    progress.console.print(
                        f"[yellow]:warning: Failed attempt {attempt} to download '{filename}': {e}"
                    )
                else:
                    raise HegreError(
                        f"Failed attempt {attempt} to download {filename}: {e}"
                    )

            if failed:
                attempt += 1
                progress.update(task_id, description=f"[red strike]{filename}[/]")
                progress.stop_task(task_id)
                task_id = progress.add_task(task_prefix + filename, start=False)

        # we can assume a successful download here
        os.rename(temp_file, dest_file)

    def _download_file(
        self,
        url: str,
        dest_file: str,
        progress: Progress | None = None,
        task_id: TaskID | None = None,
        chunk_size: int = 16 * 1024,
    ):
        with self._session.get(url, stream=True) as stream:
            stream.raise_for_status()

            with open(dest_file, "wb") as file:
                content_length = int(stream.headers["Content-Length"])

                if progress and task_id != None:
                    progress.update(task_id, total=content_length)
                    progress.start_task(task_id)

                for chunk in stream.iter_content(chunk_size=chunk_size):
                    file.write(chunk)
                    if progress and task_id != None:
                        progress.update(task_id, advance=chunk_size)


def generate_movie_filename(url: str, movie: HegreMovie) -> tuple[str, str]:
    original_name = os.path.basename(urlparse(url).path)
    name, _ = os.path.splitext(original_name)

    if movie.date:
        date_str = movie.date.strftime("%Y.%m.%d")

        return (
            f"{date_str}-{movie.code}-{original_name}",
            f"{date_str}-{movie.code}-{name}.json",
        )
    else:
        return (
            f"{movie.code}-{original_name}",
            f"{movie.code}-{name}.json",
        )
