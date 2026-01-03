from __future__ import annotations

from collections.abc import Iterable

from goodreads_tools.http_client import GoodreadsClient
from goodreads_tools.models import SearchItem


def parse_search_results(payload: Iterable[dict]) -> list[SearchItem]:
    results: list[SearchItem] = []
    for item in payload:
        results.append(SearchItem.model_validate(item))
    return results


def search_books(query: str, client: GoodreadsClient | None = None) -> list[SearchItem]:
    close_client = False
    if client is None:
        client = GoodreadsClient()
        close_client = True
    try:
        payload = client.get_json(
            "/book/auto_complete",
            params={"format": "json", "q": query},
        )
        if not isinstance(payload, list):
            raise ValueError("Unexpected search response shape.")
        return parse_search_results(payload)
    finally:
        if close_client:
            client.close()
