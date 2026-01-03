from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import UTC
from email.utils import parsedate_to_datetime
from typing import Literal

from goodreads_tools.http_client import GoodreadsClient
from goodreads_tools.models import ReadingTimelineEntry, ShelfItem
from goodreads_tools.public.book import get_book_details
from goodreads_tools.public.review_list import get_review_list_timeline
from goodreads_tools.public.shelf import get_shelf_items

StartDateSource = Literal["auto", "started", "added", "created"]
TimelineSource = Literal["rss", "html"]


def _to_iso(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if parsed is None:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.isoformat()


def _pick_start_date(item: ShelfItem, source: StartDateSource) -> str | None:
    if source == "started":
        return item.date_started
    if source == "added":
        return item.date_added
    if source == "created":
        return item.date_created
    return item.date_started or item.date_added or item.date_created


def build_reading_timeline(
    items: Iterable[ShelfItem],
    start_source: StartDateSource = "auto",
    page_overrides: dict[str, int | None] | None = None,
) -> list[ReadingTimelineEntry]:
    entries: list[ReadingTimelineEntry] = []
    overrides = page_overrides or {}
    for item in items:
        pages = overrides.get(item.book_id, item.pages)
        entries.append(
            ReadingTimelineEntry(
                title=item.title,
                book_id=item.book_id,
                pages=pages,
                started_at=_to_iso(_pick_start_date(item, start_source)),
                finished_at=_to_iso(item.read_at),
                shelves=item.shelves,
            )
        )
    return entries


def _resolve_pages(
    items: Iterable[ShelfItem],
    client: GoodreadsClient,
) -> dict[str, int | None]:
    resolved: dict[str, int | None] = {}
    for item in items:
        if item.book_id in resolved:
            continue
        if item.pages is not None:
            resolved[item.book_id] = item.pages
            continue
        details = get_book_details(item.book_id, client=client)
        resolved[item.book_id] = details.pages
    return resolved


def _resolve_entry_pages(
    entries: Iterable[ReadingTimelineEntry],
    client: GoodreadsClient,
) -> list[ReadingTimelineEntry]:
    resolved: dict[str, int | None] = {}
    resolved_entries: list[ReadingTimelineEntry] = []
    for entry in entries:
        pages = entry.pages
        if pages is None:
            if entry.book_id not in resolved:
                details = get_book_details(entry.book_id, client=client)
                resolved[entry.book_id] = details.pages
            pages = resolved[entry.book_id]
        resolved_entries.append(entry.model_copy(update={"pages": pages}))
    return resolved_entries


def get_reading_timeline(
    user_id: str,
    shelf: str,
    client: GoodreadsClient | None = None,
    *,
    source: TimelineSource = "rss",
    start_source: StartDateSource = "auto",
    resolve_pages: bool = False,
    max_pages: int | None = None,
) -> list[ReadingTimelineEntry]:
    close_client = False
    if client is None:
        client = GoodreadsClient()
        close_client = True
    try:
        if source == "html":
            entries = get_review_list_timeline(
                user_id,
                shelf,
                client=client,
                max_pages=max_pages,
            )
            return _resolve_entry_pages(entries, client) if resolve_pages else entries
        items = list(get_shelf_items(user_id, shelf, client=client))
        page_overrides = _resolve_pages(items, client) if resolve_pages else None
        return build_reading_timeline(
            items,
            start_source=start_source,
            page_overrides=page_overrides,
        )
    finally:
        if close_client:
            client.close()


def timeline_entries_to_json(entries: Iterable[ReadingTimelineEntry]) -> str:
    payload = [entry.model_dump() for entry in entries]
    return json.dumps(payload)


def timeline_entries_to_jsonl(entries: Iterable[ReadingTimelineEntry]) -> str:
    return "\n".join(json.dumps(entry.model_dump()) for entry in entries)
