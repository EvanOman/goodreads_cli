import json
from pathlib import Path

from goodreads_tools.public.search import parse_search_results


def test_parse_search_results() -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "search_dune.json"
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    results = parse_search_results(payload)

    assert results
    first = results[0]
    assert first.book_id
    assert first.title
    assert first.book_url.startswith("/book/show/")
    assert first.author is not None
    assert first.author.name
