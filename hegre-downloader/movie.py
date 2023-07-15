from __future__ import annotations

from bs4 import BeautifulSoup
from bs4.element import Tag

from datetime import datetime, date

import os
import re
import json

from model import HegreModel
from helper import HegreJSONEncoder


class HegreMovie:
    title: str
    code: int
    url: str
    duration: int

    cover_url: str
    date: date
    description: str
    models: list[HegreModel]
    downloads: dict[int, str]

    def __init__(self) -> None:
        self.models = list()
        self.downloads = dict()

    def __str__(self) -> str:
        return f"{self.title} [code: {self.code}, duration: {self.duration}s]"

    @staticmethod
    def from_films_listing(films_item: Tag) -> HegreMovie:
        hm = HegreMovie()

        hm.title = films_item.select_one("a").attrs["title"]
        hm.code = int(films_item.select_one("a").attrs["data-id"])
        hm.url = "https://www.hegre.com" + films_item.select_one("a").attrs["href"]
        hm.duration = HegreMovie.duration_to_seconds(
            films_item.select_one(".right").text.strip()
        )

        return hm

    def parse_details_from_film_page(self, film_page: BeautifulSoup) -> None:
        # cover image
        bg_image_url = film_page.select_one(".video-player-wrapper").attrs["style"]
        if url_result := re.search(r"(http.*)\?", bg_image_url):
            self.cover_url = url_result.group(1)

        self.description = film_page.select_one(".massage-copy").text.strip()
        self.date = datetime.strptime(film_page.select_one(".date").text, "%B %d, %Y")

        models = film_page.select(".record-model")
        for model in models:
            url = "https://www.hegre.com" + model.attrs["href"]
            name = model.attrs["title"]
            self.models.append(HegreModel(name, url))

        download_links = film_page.select(".content a")
        for download_link in download_links:
            url = re.search(r"(http.*)\?", download_link.attrs["href"]).group(1)
            res = int(re.search(r"(\d{3,4})p", download_link.text).group(1))
            self.downloads.setdefault(res, url)

    def get_highest_res_download_url(self) -> tuple[int, str]:
        sorted_resolutions = sorted(self.downloads, reverse=True)
        return (sorted_resolutions[0], self.downloads[sorted_resolutions[0]])

    def get_download_url_for_res(self, res: int | None = None) -> tuple[int, str]:
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
