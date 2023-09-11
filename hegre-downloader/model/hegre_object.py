from typing import Optional
from datetime import date

from model.object_type import ObjectType
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
        raise NotImplementedError()

    def get_download_url_for_res(self, res: Optional[int] = None) -> tuple[int, str]:
        raise NotImplementedError()

    def write_metadata_file(self, destination_folder: str, filename: str) -> None:
        raise NotImplementedError()
