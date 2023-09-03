from __future__ import annotations

from datetime import datetime, date
from typing import Optional
import re

from bs4 import BeautifulSoup

from object_type import ObjectType
from model import HegreModel
from exceptions import HegreError


class HegreGallery:
    url: str
    type: ObjectType

    title: Optional[str]
    code: Optional[int]
    date: Optional[date]

    tags: list[str]
    models: list[HegreModel]
    downloads: dict[int, str]

    def __init__(self, url: str) -> None:
        self.url = url
        self.type = ObjectType.PHOTOS

        self.title = None
        self.code = None
        self.date = None

        self.tags = list()
        self.models = list()
        self.downloads = dict()

    def __str__(self) -> str:
        return f"{self.date} {self.title} [{self.code}]"

    @staticmethod
    def from_gallery_page(url: str, gallery_page: BeautifulSoup) -> HegreGallery:
        hg = HegreGallery(url)

        if re.match(r"^https?:\/\/www\.hegre\.com\/photos\/", url):
            hg._parse_details_from_gallery_page(gallery_page)
        else:
            raise HegreError(f"Unsupported gallry URL {url}")

        return hg

    def _parse_details_from_gallery_page(self, gallery_page: BeautifulSoup) -> None:
        self.title = gallery_page.select_one("h1.translated-text").text.strip()
        self.code = int(gallery_page.select_one(".comments-wrapper").attrs["data-id"])
        self.date = datetime.strptime(
            gallery_page.select_one(".date").text, "%B %d, %Y"
        ).date()

        # models
        models = gallery_page.select(".record-model")
        for model in models:
            url = "https://www.hegre.com" + model.attrs["href"]
            name = model.attrs["title"]
            self.models.append(HegreModel(name, url))

        # tags
        tags = gallery_page.select(".approved-tags > .tag")
        for tag in tags:
            self.tags.append(tag.text.strip().title())

        # downloads
        links = gallery_page.select(".gallery-zips > .members-only")
        for link in links:
            url = link.attrs["href"]
            url = re.search(r"(http.*)\?", url).group(1)  # remove all parameters
            px = re.search(r"-(\d{4,5})px", url).group(1)

            self.downloads.setdefault(px, url)
