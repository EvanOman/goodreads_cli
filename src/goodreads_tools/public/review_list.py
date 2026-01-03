from __future__ import annotations

import re
from datetime import datetime
from urllib.parse import urljoin

from selectolax.parser import HTMLParser, Node

from goodreads_tools.http_client import DEFAULT_BASE_URL, GoodreadsClient
from goodreads_tools.models import ReadingTimelineEntry

_DATE_FORMATS = ("%b %d, %Y", "%B %d, %Y", "%b %Y", "%B %Y", "%Y")


def _parse_human_date(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _extract_book_id(href: str | None) -> str:
    if not href:
        return ""
    match = re.search(r"/book/show/(\d+)", href)
    return match.group(1) if match else ""


def _extract_pages(text: str | None) -> int | None:
    if not text:
        return None
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else None


def _extract_session_id(classes: str, prefix: str) -> str | None:
    for name in classes.split():
        if name.startswith(prefix):
            return name[len(prefix) :]
    return None


def _parse_session_dates(
    cell: Node, field: str, value_class: str
) -> tuple[dict[str, str], list[str]]:
    sessions: dict[str, str] = {}
    order: list[str] = []
    prefix = f"{field}_"
    for node in cell.css("div.editable_date"):
        classes = node.attributes.get("class") or ""
        session_id = _extract_session_id(classes, prefix)
        if not session_id:
            continue
        value = None
        span = node.css_first(f"span.{value_class}")
        if span is not None:
            value = _parse_human_date(span.text(strip=True))
        if value:
            sessions[session_id] = value
            order.append(session_id)
    return sessions, order


def parse_review_list_html(html: str, shelf: str | None = None) -> list[ReadingTimelineEntry]:
    parser = HTMLParser(html)
    entries: list[ReadingTimelineEntry] = []

    for row in parser.css("tr.bookalike"):
        title_node = row.css_first("td.field.title a")
        title = title_node.text(strip=True) if title_node else ""
        book_id = _extract_book_id(title_node.attributes.get("href") if title_node else None)
        pages_node = row.css_first("td.field.num_pages")
        pages = _extract_pages(pages_node.text(strip=True) if pages_node else None)

        started_node = row.css_first("td.field.date_started")
        read_node = row.css_first("td.field.date_read")

        started_sessions, started_order = (
            _parse_session_dates(started_node, "date_started", "date_started_value")
            if started_node
            else ({}, [])
        )
        read_sessions, read_order = (
            _parse_session_dates(read_node, "date_read", "date_read_value")
            if read_node
            else ({}, [])
        )
        session_ids: list[str] = []
        seen: set[str] = set()
        for session_id in started_order + read_order:
            if session_id in seen:
                continue
            seen.add(session_id)
            session_ids.append(session_id)
        shelves = [shelf] if shelf else []

        if not session_ids:
            entries.append(
                ReadingTimelineEntry(
                    title=title,
                    book_id=book_id,
                    pages=pages,
                    started_at=None,
                    finished_at=None,
                    shelves=shelves,
                )
            )
            continue

        for session_id in session_ids:
            entries.append(
                ReadingTimelineEntry(
                    title=title,
                    book_id=book_id,
                    pages=pages,
                    started_at=started_sessions.get(session_id),
                    finished_at=read_sessions.get(session_id),
                    shelves=shelves,
                )
            )

    return entries


def _find_next_page(html: str) -> str | None:
    parser = HTMLParser(html)
    link = parser.css_first("a.next_page")
    if link is None:
        return None
    classes = link.attributes.get("class") or ""
    if "disabled" in classes:
        return None
    href = link.attributes.get("href")
    return href


def get_review_list_timeline(
    user_id: str,
    shelf: str,
    client: GoodreadsClient | None = None,
    *,
    max_pages: int | None = None,
) -> list[ReadingTimelineEntry]:
    close_client = False
    if client is None:
        client = GoodreadsClient()
        close_client = True

    try:
        entries: list[ReadingTimelineEntry] = []
        page_url = f"/review/list/{user_id}"
        params = {"shelf": shelf, "sort": "date_read", "order": "d"}
        page_count = 0

        while True:
            html = client.get_text(page_url, params=params)
            entries.extend(parse_review_list_html(html, shelf=shelf))
            page_count += 1
            if max_pages is not None and page_count >= max_pages:
                break
            next_href = _find_next_page(html)
            if not next_href:
                break
            page_url = urljoin(DEFAULT_BASE_URL, next_href)
            params = None
        return entries
    finally:
        if close_client:
            client.close()
