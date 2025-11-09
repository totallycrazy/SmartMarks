"""Importer for Netscape-style bookmark HTML exports."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from bs4 import BeautifulSoup

from ..schemas import BookmarkCreate


class BookmarkHtmlImporter:
    """Parse exported bookmark HTML files into BookmarkCreate payloads."""

    def __init__(self, default_source: str | None = "html-import") -> None:
        self.default_source = default_source

    def parse(self, raw_html: str) -> Iterable[BookmarkCreate]:
        soup = BeautifulSoup(raw_html, "html.parser")
        for anchor in soup.find_all("a"):
            href = anchor.get("href")
            title = anchor.get_text(strip=True) or href
            tags = []
            if anchor.has_attr("tags"):
                tags = [tag.strip() for tag in anchor["tags"].split(",") if tag.strip()]
            add_date = anchor.get("add_date")
            created = None
            if add_date and add_date.isdigit():
                created = datetime.fromtimestamp(int(add_date))

            metadata = {
                "url": href,
                "title": title or href,
                "description": anchor.get("description"),
                "tags": tags,
                "source": self.default_source,
            }
            if not metadata["url"]:
                continue
            yield BookmarkCreate(**metadata)

    def parse_file(self, path: str) -> List[BookmarkCreate]:
        with open(path, "r", encoding="utf-8") as handle:
            return list(self.parse(handle.read()))
