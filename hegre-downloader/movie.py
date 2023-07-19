from __future__ import annotations

from bs4 import BeautifulSoup

from datetime import datetime, date
from typing import Optional
from enum import Enum

import os
import re
import json

from model import HegreModel
from exceptions import HegreError
from helper import HegreJSONEncoder


class MovieType(Enum):
    FILM = "films"
    MASSAGE = "massage"
    SEXED = "sexed"

    def __str__(self) -> str:
        return self.value

    @staticmethod
    def from_str(type_str: str) -> MovieType:
        match type_str:
            case MovieType.FILM.value:
                return MovieType.FILM
            case MovieType.MASSAGE.value:
                return MovieType.MASSAGE
            case MovieType.SEXED.value:
                return MovieType.SEXED
            case _:
                raise ValueError(f"Invalid movie type string '{type_str}'")


class HegreMovie:
    url: str

    title: Optional[str]
    code: Optional[int]
    duration: Optional[int]
    cover_url: Optional[str]
    date: Optional[date]
    description: Optional[str]
    type: Optional[MovieType]

    tags: list[str]
    models: list[HegreModel]
    downloads: dict[int, str]

    def __init__(self, url: str) -> None:
        self.url = url

        self.title = None
        self.code = None
        self.duration = None
        self.cover_url = None
        self.date = None
        self.description = None
        self.type = None

        self.tags = list()
        self.models = list()
        self.downloads = dict()

    def __str__(self) -> str:
        return f"{self.title} [code: {self.code}, duration: {self.duration}s]"

    @staticmethod
    def from_film_page(url: str, film_page: BeautifulSoup) -> HegreMovie:
        hm = HegreMovie(url)

        if match := re.match(r"^https?:\/\/www\.hegre\.com\/(films|massage)\/", url):
            type = MovieType.from_str(match.group(1))
            hm.parse_details_from_films_or_massage_page(type, film_page)
        elif re.match(r"^https?:\/\/www\.hegre\.com\/sexed\/", url):
            hm.parse_details_from_sexed_page(film_page)
        else:
            raise HegreError(f"Unsupported movie URL {url}")

        return hm

    def parse_details_from_sexed_page(self, film_page: BeautifulSoup) -> None:
        self.title = film_page.select_one(".film-header > h1").text.strip()
        self.code = int(film_page.select_one(".comments-wrapper").attrs["data-id"])
        self.duration = HegreMovie.duration_to_seconds(
            film_page.select_one(".film-header > div > strong").text.split()[0]
        )
        self.description = film_page.select_one(".film-header .intro").text.strip()
        self.type = MovieType.SEXED
        # no upload date available!
        # no models available!

        # cover image
        bg_image_url = film_page.select_one(".video-player-wrapper").attrs["style"]
        if url_result := re.search(r"(http.*)\?", bg_image_url):
            self.cover_url = url_result.group(1)

        # download links
        video_player_script = film_page.select_one(".top script").text
        if video_player_raw_json := re.search(r'({".*)\);', video_player_script):
            video_player_json = json.loads(video_player_raw_json.group(1))
            resolutions = video_player_json["resolutions"]

            for resolution in resolutions:
                res = resolution["type"]
                url = resolution["sources"]["default"][0]["mp4"]
                url = re.search(r"(http.*)\?", url).group(1)  # remove all parameters
                self.downloads.setdefault(res, url)

        # tags
        tags = film_page.select(".approved-tags > .tag")
        for tag in tags:
            self.tags.append(tag.text.strip().title())

    def parse_details_from_films_or_massage_page(
        self, type: MovieType, film_page: BeautifulSoup
    ) -> None:
        self.type = type
        self.title = film_page.select_one(".title > .translated-text").text.strip()
        self.code = int(film_page.select_one(".comments-wrapper").attrs["data-id"])
        self.duration = HegreMovie.duration_to_seconds(
            film_page.select_one(".format-details").text.split()[1]
        )
        self.description = film_page.select_one(".massage-copy").text.strip()
        self.date = datetime.strptime(film_page.select_one(".date").text, "%B %d, %Y")

        # cover image
        bg_image_url = film_page.select_one(".video-player-wrapper").attrs["style"]
        if url_result := re.search(r"(http.*)\?", bg_image_url):
            self.cover_url = url_result.group(1)

        # models
        models = film_page.select(".record-model")
        for model in models:
            url = "https://www.hegre.com" + model.attrs["href"]
            name = model.attrs["title"]
            self.models.append(HegreModel(name, url))

        # download URLs
        download_links = film_page.select(".content a")
        for download_link in download_links:
            url = re.search(r"(http.*)\?", download_link.attrs["href"]).group(1)
            res = int(re.search(r"(\d{3,4})p", download_link.text).group(1))
            self.downloads.setdefault(res, url)

        # tags
        tags = film_page.select(".approved-tags > .tag")
        for tag in tags:
            self.tags.append(tag.text.strip().title())

    def get_highest_res_download_url(self) -> tuple[int, str]:
        sorted_resolutions = sorted(self.downloads, reverse=True)
        return (sorted_resolutions[0], self.downloads[sorted_resolutions[0]])

    def get_download_url_for_res(self, res: Optional[int] = None) -> tuple[int, str]:
        if res and res not in self.downloads:
            raise KeyError(
                f"Resolution {res}p is not available! Available resolutions are: {','.join(self.downloads.keys())}"
            )
        elif res:
            url = self.downloads[res]
        else:
            res, url = self.get_highest_res_download_url()

        return res, url

    def write_metadata_file(self, destination_folder: str, filename: str) -> None:
        metadata_file = os.path.join(destination_folder, filename)

        with open(metadata_file, "w") as file:
            file.write(json.dumps(self, sort_keys=True, indent=4, cls=HegreJSONEncoder))

    @staticmethod
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
                return (
                    int(elements[0]) * 3600 + int(elements[1]) * 60 + int(elements[2])
                )
            case 2:
                return int(elements[0]) * 60 + int(elements[1])
            case 1:
                return int(elements[0])
            case _:
                raise ValueError("Could not parse duration string into seconds")
