from typing import Optional
from datetime import date, datetime
import json
import os
import re

from bs4 import BeautifulSoup

from model.object_type import ObjectType
from hegre_json_encoder import HegreJSONEncoder
from model.model import HegreModel


class HegreObject:
    url: str
    type: ObjectType

    title: Optional[str]
    code: Optional[int]
    date: Optional[date]
    cover_url: Optional[str]
    tags: list[str]
    models: list[HegreModel]
    downloads: dict[int, str]

    def __init__(self, url: str, type: ObjectType) -> None:
        self.url = url
        self.type = type

        self.tags = list()
        self.models = list()
        self.downloads = dict()

    def __str__(self) -> str:
        return f"{self.date} {self.title} [{self.code}]"

    def archive_id(self) -> str:
        return f"{self.type} {self.code}"

    def get_highest_res_download_url(self) -> tuple[int, str]:
        sorted_resolutions = sorted(self.downloads, reverse=True)
        return (sorted_resolutions[0], self.downloads[sorted_resolutions[0]])

    def get_download_url_for_res(self, res: Optional[int] = None) -> tuple[int, str]:
        if res and res not in self.downloads:
            raise KeyError(
                f"Resolution {res}p/px is not available! Available resolutions are: {','.join(map(str, self.downloads.keys()))}"
            )
        elif res:
            url = self.downloads[res]
        else:
            res, url = self.get_highest_res_download_url()

        return res, url

    def write_metadata_file(self, destination_folder: str, filename: str) -> None:
        metadata_file = os.path.join(destination_folder, filename)

        with open(metadata_file, "w", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    self,
                    sort_keys=True,
                    indent=4,
                    ensure_ascii=False,
                    cls=HegreJSONEncoder,
                )
            )


DATE_FORMATS = ("%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%Y-%m-%d")


def parse_date(page: BeautifulSoup) -> Optional[date]:
    """Returns the upload date of a movie/gallery page or None if it is not shown"""
    for element in page.select(".date, time[datetime]"):
        if iso_date := element.attrs.get("datetime"):
            text = iso_date[:10]  # strip time, e.g. "2024-05-01T12:00:00Z"
        else:
            text = " ".join(element.text.split())

        for date_format in DATE_FORMATS:
            try:
                return datetime.strptime(text, date_format).date()
            except ValueError:
                pass

    return None


def parse_models(page: BeautifulSoup) -> list[HegreModel]:
    models = []

    for model in page.select(".record-model"):
        url = "https://www.hegre.com" + model.attrs["href"]
        name = model.attrs.get("title") or model.text.strip()
        models.append(HegreModel(name, url))

    return models


def parse_tags(page: BeautifulSoup) -> list[str]:
    return [tag.text.strip().title() for tag in page.select(".approved-tags > .tag")]
