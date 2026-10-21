from __future__ import annotations

import re

from bs4 import BeautifulSoup

from model.object_type import ObjectType
from model.hegre_object import HegreObject, parse_date, parse_models, parse_tags
from helper import strip_query, extract_css_url
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

        if not re.match(r"^https?:\/\/www\.hegre\.com\/photos\/", url):
            raise HegreError(f"Unsupported gallery URL {url}")

        try:
            hg._parse_details_from_gallery_page(gallery_page)
        except (AttributeError, KeyError, ValueError) as e:
            raise HegreError(
                f"Could not parse gallery page {url} (the site layout may have changed): {e!r}"
            ) from e

        return hg

    def _parse_details_from_gallery_page(self, gallery_page: BeautifulSoup) -> None:
        self.title = gallery_page.select_one("h1.translated-text").text.strip()
        self.code = int(gallery_page.select_one(".comments-wrapper").attrs["data-id"])
        # the upload date is no longer shown on the public page, so it may be missing
        self.date = parse_date(gallery_page)

        self.models = parse_models(gallery_page)
        self.tags = parse_tags(gallery_page)

        # downloads
        links = gallery_page.select(".gallery-zips > .members-only")
        for link in links:
            url = strip_query(link.attrs["href"])
            if px_match := re.search(r"-(\d{3,5})px", url):
                self.downloads.setdefault(int(px_match.group(1)), url)

        # cover image
        if cover := gallery_page.select_one(".record-content > .non-members"):
            self.cover_url = extract_css_url(cover.attrs.get("style"))
