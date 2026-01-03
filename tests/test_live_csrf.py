import os

import pytest

from goodreads_tools.auth.csrf import fetch_csrf_token
from goodreads_tools.auth.session import create_session_from_cookie_string
from goodreads_tools.http_client import GoodreadsClient


@pytest.mark.live
def test_live_csrf_token() -> None:
    if os.getenv("GOODREADS_LIVE") != "1":
        pytest.skip("Set GOODREADS_LIVE=1 to run live tests.")
    cookie_string = os.getenv("GOODREADS_COOKIE") or ""
    if not cookie_string:
        pytest.skip("Set GOODREADS_COOKIE to run CSRF live test.")
    session = create_session_from_cookie_string(cookie_string)
    client = GoodreadsClient(cookies=session.cookies)
    token = fetch_csrf_token(client)
    client.close()
    assert token
