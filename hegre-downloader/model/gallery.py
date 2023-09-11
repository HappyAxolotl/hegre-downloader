from __future__ import annotations

from datetime import datetime
import re

from bs4 import BeautifulSoup

from model.object_type import ObjectType
from model.model import HegreModel
from model.hegre_object import HegreObject
from exceptions import HegreError


class HegreGallery(HegreObject):
    def __init__(self, url: str) -> None:
        self.url = url
        self.type = ObjectType.PHOTOS

        self.title = None
        self.code = None
        self.date = None
        self.cover_url = None

        self.tags = list()
        self.models = list()
        self.downloads = dict()

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
            px = int(re.search(r"-(\d{4,5})px", url).group(1))

            self.downloads.setdefault(px, url)

        # cover image
        bg_image_url = gallery_page.select_one(".record-content > .non-members").attrs[
            "style"
        ]
        if url_result := re.search(r"(http.*)\?", bg_image_url):
            self.cover_url = url_result.group(1)
