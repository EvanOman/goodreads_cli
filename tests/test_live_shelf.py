import os

import pytest

from goodreads_tools.public.shelf import get_shelf_items


@pytest.mark.live
def test_live_shelf() -> None:
    if os.getenv("GOODREADS_LIVE") != "1":
        pytest.skip("Set GOODREADS_LIVE=1 to run live tests.")
    items = get_shelf_items("1", "all")
    assert items
