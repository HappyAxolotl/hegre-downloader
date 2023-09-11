from __future__ import annotations

from bs4 import BeautifulSoup

from datetime import datetime
from typing import Optional

import re
import json

from model.model import HegreModel
from model.object_type import ObjectType
from model.hegre_object import HegreObject
from helper import duration_to_seconds
from exceptions import HegreError


class HegreMovie(HegreObject):
    duration: Optional[int]
    screengrabs_url: Optional[str]
    description: Optional[str]

    subtitles: dict[str, str]
    trailers: dict[int, str]

    def __init__(self, url: str) -> None:
        self.url = url

        self.title = None
        self.code = None
        self.duration = None
        self.cover_url = None
        self.screengrabs_url = None
        self.date = None
        self.description = None
        self.type = None

        self.tags = list()
        self.models = list()
        self.downloads = dict()
        self.subtitles = dict()
        self.trailers = dict()

    @staticmethod
    def from_film_page(url: str, film_page: BeautifulSoup) -> HegreMovie:
        hm = HegreMovie(url)

        if match := re.match(r"^https?:\/\/www\.hegre\.com\/(films|massage)\/", url):
            type = ObjectType.from_str(match.group(1))
            hm.parse_details_from_films_or_massage_page(type, film_page)
        elif re.match(r"^https?:\/\/www\.hegre\.com\/sexed\/", url):
            hm.parse_details_from_sexed_page(film_page)
        else:
            raise HegreError(f"Unsupported movie URL {url}")

        return hm

    def parse_details_from_sexed_page(self, film_page: BeautifulSoup) -> None:
        self.title = film_page.select_one(".film-header > h1").text.strip()
        self.code = int(film_page.select_one(".comments-wrapper").attrs["data-id"])
        self.duration = duration_to_seconds(
            film_page.select_one(".film-header > div > strong").text.split()[0]
        )
        self.description = film_page.select_one(".film-header .intro").text.strip()
        self.type = ObjectType.SEXED
        # no upload date available!
        # no models available!

        # cover image
        bg_image_url = film_page.select_one(".video-player-wrapper").attrs["style"]
        if url_result := re.search(r"(http.*)\?", bg_image_url):
            self.cover_url = url_result.group(1)

        # download URLs & subtitles
        video_player_script = film_page.select_one(".top script").text
        self._extract_downloads_subtitles_from_video_player(video_player_script)

        # tags
        tags = film_page.select(".approved-tags > .tag")
        for tag in tags:
            self.tags.append(tag.text.strip().title())

        # screengrabs
        if len(self.downloads) > 0:
            # replace the resolution and the .mp4 ending with .zip to download screengrabs for sexed movies
            _, url = next(iter(self.downloads.items()))
            self.screengrabs_url = re.sub(r"-\d{2,4}p\.mp4$", ".zip", url)

        # trailer URLs
        for res, download_url in self.downloads.items():
            res_str = f"{res}p"
            trailer_url = download_url.replace("c.hegre.com", "p.hegre.com")
            trailer_url = trailer_url.replace(res_str, f"trailer-{res_str}")

            self.trailers.setdefault(res, trailer_url)

    def parse_details_from_films_or_massage_page(
        self, type: ObjectType, film_page: BeautifulSoup
    ) -> None:
        self.type = type
        self.title = film_page.select_one(".title > .translated-text").text.strip()
        self.code = int(film_page.select_one(".comments-wrapper").attrs["data-id"])
        self.duration = duration_to_seconds(
            film_page.select_one(".format-details").text.split()[1]
        )
        self.description = film_page.select_one(".massage-copy").text.strip()
        self.date = datetime.strptime(
            film_page.select_one(".date").text, "%B %d, %Y"
        ).date()

        # cover image
        bg_image_url = film_page.select_one(".video-player-wrapper").attrs["style"]
        if url_result := re.search(r"(http.*)\?", bg_image_url):
            self.cover_url = url_result.group(1)

        # screengrabs
        screengrabs_element = film_page.select_one(".video-stills > a")
        if screengrabs_element:
            if url_result := re.search(
                r"(http.*)\?", screengrabs_element.attrs["href"]
            ):
                self.screengrabs_url = url_result.group(1)

        # models
        models = film_page.select(".record-model")
        for model in models:
            url = "https://www.hegre.com" + model.attrs["href"]
            name = model.attrs["title"]
            self.models.append(HegreModel(name, url))

        # download URLs & subtitles
        video_player_script = film_page.select_one(".video-inner > script").text
        self._extract_downloads_subtitles_from_video_player(video_player_script)

        # tags
        tags = film_page.select(".approved-tags > .tag")
        for tag in tags:
            self.tags.append(tag.text.strip().title())

        # trailer URLs
        trailers = film_page.select(".trailer > a")
        for trailer in trailers:
            res_text = trailer.select_one("strong").text
            res = int(re.search(r"(\d{3,4})p", res_text).group(1))

            url = re.search(r"(http.*)\?", trailer.attrs["href"]).group(1)
            self.trailers.setdefault(res, url)

    def _extract_downloads_subtitles_from_video_player(
        self, video_player_script: str
    ) -> None:
        if video_player_raw_json := re.search(r'({".*)\);', video_player_script):
            video_player_json = json.loads(video_player_raw_json.group(1))
            resolutions = video_player_json["resolutions"]

            for resolution in resolutions:
                res = resolution["type"]
                url = resolution["sources"]["default"][0]["mp4"]
                url = re.search(r"(http.*)\?", url).group(1)  # remove all parameters
                self.downloads.setdefault(res, url)

            subtitles: list[dict[str, str]] = video_player_json["clip"]["subtitles"]
            for subtitle in subtitles:
                label = subtitle["label"].lower()
                url = subtitle["src"]
                url = re.search(r"(http.*)\?", url).group(1)  # remove all parameters
                self.subtitles.setdefault(label, url)

    def get_subtitle_download_urls(self, languages: list[str]) -> list[str]:
        urls = []

        for lang, url in self.subtitles.items():
            if lang in languages:
                urls.append(url)

        return urls

    def get_highest_res_trailer_download_url(self) -> tuple[int, str]:
        sorted_resolutions = sorted(self.trailers, reverse=True)
        return (sorted_resolutions[0], self.trailers[sorted_resolutions[0]])

    def get_trailer_download_url_for_res(
        self, res: Optional[int] = None
    ) -> tuple[int, str]:
        if res and res not in self.trailers:
            raise KeyError(
                f"Resolution {res}p is not available! Available resolutions are: {','.join(self.trailers.keys())}"
            )
        elif res:
            url = self.trailers[res]
        else:
            res, url = self.get_highest_res_trailer_download_url()

        return res, url
