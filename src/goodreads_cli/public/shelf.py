from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterable
from xml.etree import ElementTree

from goodreads_cli.http_client import GoodreadsClient
from goodreads_cli.models import ShelfItem


def _text(node: ElementTree.Element | None) -> str | None:
    if node is None:
        return None
    value = node.text or ""
    value = value.strip()
    return value or None


def _float(value: str | None) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _int(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _split_shelves(value: str | None) -> list[str]:
    if not value:
        return []
    parts = [item.strip() for item in value.split(",")]
    return [item for item in parts if item]


def parse_shelf_rss(xml_text: str) -> list[ShelfItem]:
    root = ElementTree.fromstring(xml_text)
    items: list[ShelfItem] = []
    for item in root.findall(".//item"):
        pages = _int(_text(item.find("book/num_pages")))
        if pages is None:
            pages = _int(_text(item.find("num_pages")))
        items.append(
            ShelfItem(
                title=_text(item.find("title")) or "",
                link=_text(item.find("link")) or "",
                book_id=_text(item.find("book_id")) or "",
                author=_text(item.find("author_name")),
                average_rating=_float(_text(item.find("average_rating"))),
                rating=_int(_text(item.find("user_rating"))),
                read_at=_text(item.find("user_read_at")),
                date_added=_text(item.find("user_date_added")),
                date_created=_text(item.find("user_date_created")),
                date_started=_text(item.find("user_date_started")),
                shelves=_split_shelves(_text(item.find("user_shelves"))),
                review=_text(item.find("user_review")),
                image_url=_text(item.find("book_image_url")),
                book_published=_text(item.find("book_published")),
                pages=pages,
                isbn=_text(item.find("isbn")),
            )
        )
    return items


def _normalize_shelf(value: str) -> str:
    cleaned = value.strip().lower()
    if cleaned in {"all", "#all#", "%23all%23"}:
        return "#ALL#"
    return value


def get_shelf_items(
    user_id: str,
    shelf: str,
    client: GoodreadsClient | None = None,
) -> list[ShelfItem]:
    close_client = False
    if client is None:
        client = GoodreadsClient()
        close_client = True
    try:
        shelf_param = _normalize_shelf(shelf)
        xml_text = client.get_text(
            f"/review/list_rss/{user_id}",
            params={"shelf": shelf_param},
        )
        return parse_shelf_rss(xml_text)
    finally:
        if close_client:
            client.close()


def shelf_items_to_json(items: Iterable[ShelfItem]) -> str:
    payload = [item.model_dump() for item in items]
    return json.dumps(payload)


def shelf_items_to_csv(items: Iterable[ShelfItem]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "title",
            "author",
            "book_id",
            "link",
            "rating",
            "average_rating",
            "read_at",
            "date_added",
            "date_created",
            "date_started",
            "shelves",
            "book_published",
            "pages",
            "isbn",
            "image_url",
        ]
    )
    for item in items:
        writer.writerow(
            [
                item.title,
                item.author or "",
                item.book_id,
                item.link,
                item.rating if item.rating is not None else "",
                item.average_rating if item.average_rating is not None else "",
                item.read_at or "",
                item.date_added or "",
                item.date_created or "",
                item.date_started or "",
                ",".join(item.shelves),
                item.book_published or "",
                item.pages if item.pages is not None else "",
                item.isbn or "",
                item.image_url or "",
            ]
        )
    return output.getvalue()
