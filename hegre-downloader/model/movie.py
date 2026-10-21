from __future__ import annotations

from bs4 import BeautifulSoup

from typing import Optional

import re
import json

from model.model import HegreModel
from model.object_type import ObjectType
from model.hegre_object import HegreObject, parse_date, parse_models, parse_tags
from helper import duration_to_seconds, strip_query, extract_css_url
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

        try:
            if match := re.match(
                r"^https?:\/\/www\.hegre\.com\/(films|massage|orgasms)\/", url
            ):
                type = ObjectType.from_str(match.group(1))
                hm.parse_details_from_films_or_massage_page(type, film_page)
            elif re.match(r"^https?:\/\/www\.hegre\.com\/sexed\/", url):
                hm.parse_details_from_sexed_page(film_page)
            else:
                raise HegreError(f"Unsupported movie URL {url}")
        except (AttributeError, KeyError, ValueError) as e:
            raise HegreError(
                f"Could not parse movie page {url} (the site layout may have changed): {e!r}"
            ) from e

        return hm

    def parse_details_from_sexed_page(self, film_page: BeautifulSoup) -> None:
        self.title = film_page.select_one(".film-header > h1").text.strip()
        self.code = int(film_page.select_one(".comments-wrapper").attrs["data-id"])
        self.duration = _parse_duration(
            film_page.select_one(".film-header > div > strong")
        )
        if intro := film_page.select_one(".film-header .intro"):
            self.description = intro.text.strip()
        self.type = ObjectType.SEXED
        # no upload date available!
        # no models available!

        # cover image
        if wrapper := film_page.select_one(".video-player-wrapper"):
            self.cover_url = extract_css_url(wrapper.attrs.get("style"))

        # download URLs & subtitles
        if video_player_script := film_page.select_one(".top script"):
            self._extract_downloads_subtitles_from_video_player(
                video_player_script.text
            )

        self.tags = parse_tags(film_page)

        # screengrabs
        if len(self.downloads) > 0:
            # replace the resolution and the .mp4 ending with .zip to download screengrabs for sexed movies
            _, url = next(iter(self.downloads.items()))
            self.screengrabs_url = re.sub(r"-\d{2,4}p\.mp4$", ".zip", url)

        # trailer URLs
        for res, download_url in self.downloads.items():
            if "-trailer-" in download_url:
                # not logged in: the video player already contains the trailers
                self.trailers.setdefault(res, download_url)
                continue

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
        self.duration = _parse_duration(film_page.select_one(".format-details"))
        if description := film_page.select_one(".massage-copy"):
            self.description = description.text.strip()
        # the upload date is no longer shown on the public page, so it may be missing
        self.date = parse_date(film_page)

        # cover image
        if wrapper := film_page.select_one(".video-player-wrapper"):
            self.cover_url = extract_css_url(wrapper.attrs.get("style"))

        # screengrabs
        if screengrabs_element := film_page.select_one(".video-stills > a"):
            self.screengrabs_url = strip_query(screengrabs_element.attrs["href"])

        self.models = parse_models(film_page)

        # download URLs & subtitles
        if video_player_script := film_page.select_one(".video-inner > script"):
            self._extract_downloads_subtitles_from_video_player(
                video_player_script.text
            )

        self.tags = parse_tags(film_page)

        # trailer URLs
        trailers = film_page.select(".trailer > a")
        for trailer in trailers:
            res_text = trailer.select_one("strong").text
            if res_match := re.search(r"(\d{3,4})p", res_text):
                self.trailers.setdefault(
                    int(res_match.group(1)), strip_query(trailer.attrs["href"])
                )

    def _extract_downloads_subtitles_from_video_player(
        self, video_player_script: str
    ) -> None:
        if json_start := re.search(r'\{\s*"', video_player_script):
            # raw_decode parses exactly one JSON object and ignores the rest of the script
            video_player_json, _ = json.JSONDecoder().raw_decode(
                video_player_script, json_start.start()
            )

            for resolution in video_player_json.get("resolutions") or []:
                res = int(resolution["type"])
                for source in resolution["sources"]["default"]:
                    if "mp4" in source:
                        self.downloads.setdefault(res, strip_query(source["mp4"]))
                        break

            clip = video_player_json.get("clip") or {}
            # "subtitles" is null if the movie has no subtitles
            subtitles: list[dict[str, str]] = clip.get("subtitles") or []
            for subtitle in subtitles:
                label = subtitle["label"].lower()
                self.subtitles.setdefault(label, strip_query(subtitle["src"]))

    def has_only_trailers(self) -> bool:
        """Without an active subscription the video player only offers trailers"""
        return len(self.downloads) > 0 and all(
            "-trailer-" in url for url in self.downloads.values()
        )

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
                f"Resolution {res}p is not available! Available resolutions are: {','.join(map(str, self.trailers.keys()))}"
            )
        elif res:
            url = self.trailers[res]
        else:
            res, url = self.get_highest_res_trailer_download_url()

        return res, url


def _parse_duration(element) -> Optional[int]:
    """Parses the first "mm:ss" or "hh:mm:ss" found in the element's text"""
    if element and (match := re.search(r"\d+(?::\d{2}){1,2}", element.text)):
        return duration_to_seconds(match.group(0))

    return None
