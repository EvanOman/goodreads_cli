from pathlib import Path

from goodreads_cli.auth.csrf import extract_csrf_token


def test_extract_csrf_token_from_fixture() -> None:
    html = (Path(__file__).parent / "fixtures" / "sign_in.html").read_text(encoding="utf-8")
    token = extract_csrf_token(html)
    assert token is not None
    assert len(token) > 10
