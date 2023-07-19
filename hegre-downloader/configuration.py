from typing import Optional
from pathlib import Path

from sort_option import SortOption


class Configuration:
    urls: list[str]
    destination_folder: Path
    retries: int
    sort: SortOption

    no_thumb: bool
    no_meta: bool
    no_subtitles: bool
    no_download: bool

    resolution: Optional[int]

    def __init__(
        self,
        urls: list[str],
        destination_folder: Path,
        retries: int,
        sort: SortOption,
        no_thumb: bool = False,
        no_meta: bool = False,
        no_subtitles: bool = False,
        no_download: bool = False,
        resolution: Optional[int] = None,
    ) -> None:
        self.urls = urls
        self.destination_folder = destination_folder
        self.retries = retries
        self.sort = sort

        self.no_thumb = no_thumb
        self.no_meta = no_meta
        self.no_subtitles = no_subtitles
        self.no_download = no_download

        self.resolution = resolution
