from pathlib import Path

from goodreads_cli.auth.session import (
    SessionData,
    load_session,
    parse_cookie_string,
    save_session,
)


def test_parse_cookie_string() -> None:
    cookies = parse_cookie_string("_session_id2=abc; ccsid=123; locale=en")
    assert cookies["_session_id2"] == "abc"
    assert cookies["ccsid"] == "123"
    assert cookies["locale"] == "en"


def test_save_and_load_session(tmp_path: Path) -> None:
    path = tmp_path / "session.json"
    session = SessionData(cookies={"a": "b"}, source="test", created_at=1.0)
    save_session(session, path)
    loaded = load_session(path)
    assert loaded.cookies == {"a": "b"}
    assert loaded.source == "test"
