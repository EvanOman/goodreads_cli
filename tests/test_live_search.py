import os

import pytest

from goodreads_cli.public.search import search_books


@pytest.mark.live
def test_live_search() -> None:
    if os.getenv("GOODREADS_LIVE") != "1":
        pytest.skip("Set GOODREADS_LIVE=1 to run live tests.")
    results = search_books("Dune")
    assert results
    assert any("Dune" in item.title for item in results)
