import os

import pytest

from goodreads_cli.public.timeline import get_reading_timeline


@pytest.mark.live
def test_live_timeline() -> None:
    if os.getenv("GOODREADS_LIVE") != "1":
        pytest.skip("Set GOODREADS_LIVE=1 to run live tests.")
    entries = get_reading_timeline("1", "all")
    assert entries
    assert any(entry.pages for entry in entries)
