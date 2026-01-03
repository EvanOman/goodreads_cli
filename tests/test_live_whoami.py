import os

import pytest

from goodreads_cli.auth.session import create_session_from_cookie_string
from goodreads_cli.auth.user import get_current_user
from goodreads_cli.http_client import GoodreadsClient


@pytest.mark.live
def test_live_whoami() -> None:
    if os.getenv("GOODREADS_LIVE") != "1":
        pytest.skip("Set GOODREADS_LIVE=1 to run live tests.")
    cookie_string = os.getenv("GOODREADS_COOKIE") or ""
    if not cookie_string:
        pytest.skip("Set GOODREADS_COOKIE to run whoami live test.")
    session = create_session_from_cookie_string(cookie_string)
    client = GoodreadsClient(cookies=session.cookies)
    user = get_current_user(client)
    client.close()
    assert user is not None
    assert user.user_id
