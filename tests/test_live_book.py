import os

import pytest

from goodreads_cli.public.book import get_book_details


@pytest.mark.live
def test_live_book_details() -> None:
    if os.getenv("GOODREADS_LIVE") != "1":
        pytest.skip("Set GOODREADS_LIVE=1 to run live tests.")
    details = get_book_details("44767458")
    assert details.title == "Dune"
