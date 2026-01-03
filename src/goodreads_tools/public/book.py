from __future__ import annotations

import json
from typing import Any

from selectolax.parser import HTMLParser

from goodreads_tools.http_client import GoodreadsClient
from goodreads_tools.models import BookDetails


def _extract_next_data(html: str) -> dict[str, Any]:
    parser = HTMLParser(html)
    script = parser.css_first("script#__NEXT_DATA__")
    if script is None:
        raise ValueError("Missing __NEXT_DATA__ payload in book page.")
    return json.loads(script.text())


def _find_book_record(apollo_state: dict[str, Any]) -> dict[str, Any]:
    for key, value in apollo_state.items():
        if key.startswith("Book:") and isinstance(value, dict):
            return value
    raise ValueError("No Book record found in apollo state.")


def _resolve_author(
    apollo_state: dict[str, Any], book: dict[str, Any]
) -> tuple[int | None, str | None]:
    primary = book.get("primaryContributorEdge") or {}
    node = primary.get("node") or {}
    ref = node.get("__ref")
    if not ref or ref not in apollo_state:
        return None, None
    author = apollo_state[ref]
    return author.get("legacyId"), author.get("name")


def _resolve_stats(
    apollo_state: dict[str, Any], book: dict[str, Any]
) -> tuple[float | None, int | None]:
    work = book.get("work") or {}
    ref = work.get("__ref")
    if not ref or ref not in apollo_state:
        return None, None
    work = apollo_state[ref]
    stats = work.get("stats") or {}
    avg = stats.get("averageRating")
    count = stats.get("ratingsCount")
    return avg, count


def _pick_description(book: dict[str, Any]) -> str | None:
    for key in ('description({"stripped":true})', "description"):
        value = book.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def parse_book_details(html: str) -> BookDetails:
    data = _extract_next_data(html)
    apollo_state = data.get("props", {}).get("pageProps", {}).get("apolloState")
    if not isinstance(apollo_state, dict):
        raise ValueError("Missing apolloState in book page.")

    book = _find_book_record(apollo_state)
    author_id, author_name = _resolve_author(apollo_state, book)
    avg_rating, ratings_count = _resolve_stats(apollo_state, book)
    details = book.get("details") or {}

    return BookDetails(
        book_id=str(book.get("legacyId") or ""),
        title=book.get("title") or "",
        url=book.get("webUrl") or "",
        image_url=book.get("imageUrl"),
        description=_pick_description(book),
        author_id=author_id,
        author_name=author_name,
        avg_rating=avg_rating,
        ratings_count=ratings_count,
        pages=details.get("numPages"),
        format=details.get("format"),
        publisher=details.get("publisher"),
        isbn=details.get("isbn"),
        isbn13=details.get("isbn13"),
        language=(details.get("language") or {}).get("name"),
    )


def _normalize_book_path(book_id_or_url: str) -> str:
    value = book_id_or_url.strip()
    if value.startswith("http://") or value.startswith("https://"):
        if "goodreads.com" not in value:
            raise ValueError("Only Goodreads URLs are supported.")
        parts = value.split("goodreads.com", 1)
        return parts[1] if parts[1].startswith("/") else f"/{parts[1]}"
    if value.startswith("/book/show/"):
        return value
    if value.startswith("book/show/"):
        return f"/{value}"
    if value.isdigit():
        return f"/book/show/{value}"
    return f"/book/show/{value}"


def get_book_details(book_id_or_url: str, client: GoodreadsClient | None = None) -> BookDetails:
    close_client = False
    if client is None:
        client = GoodreadsClient()
        close_client = True
    try:
        path = _normalize_book_path(book_id_or_url)
        html = client.get_text(path)
        return parse_book_details(html)
    finally:
        if close_client:
            client.close()
