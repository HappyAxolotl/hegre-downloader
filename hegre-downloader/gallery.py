from __future__ import annotations

from datetime import datetime, date
import json
import os
from typing import Optional
import re

from bs4 import BeautifulSoup

from object_type import ObjectType
from model import HegreModel
from exceptions import HegreError
from helper import HegreJSONEncoder


class HegreGallery:
    url: str
    type: ObjectType

    title: Optional[str]
    code: Optional[int]
    date: Optional[date]
    cover_url: Optional[str]

    tags: list[str]
    models: list[HegreModel]
    downloads: dict[int, str]

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
            px = int(re.search(r"-(\d{4,5})px", url).group(1))

            self.downloads.setdefault(px, url)

        # cover image
        bg_image_url = gallery_page.select_one(".record-content > .non-members").attrs[
            "style"
        ]
        if url_result := re.search(r"(http.*)\?", bg_image_url):
            self.cover_url = url_result.group(1)

    def get_highest_res_download_url(self) -> tuple[int, str]:
        sorted_resolutions = sorted(self.downloads, reverse=True)
        return (sorted_resolutions[0], self.downloads[sorted_resolutions[0]])

    def get_download_url_for_res(self, res: Optional[int] = None) -> tuple[int, str]:
        if res and res not in self.downloads:
            raise KeyError(
                f"Resolution {res}px is not available! Available resolutions are: {','.join(self.downloads.keys())}"
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
