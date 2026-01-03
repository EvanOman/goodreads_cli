from __future__ import annotations

import re

from selectolax.parser import HTMLParser

from goodreads_cli.http_client import GoodreadsClient

_CSRF_RE = re.compile(
    r'<meta\\s+name="csrf-token"\\s+content="([^"]+)"',
    re.IGNORECASE,
)


def extract_csrf_token(html: str) -> str | None:
    parser = HTMLParser(html)
    meta = parser.css_first('meta[name="csrf-token"]')
    if meta:
        token = meta.attributes.get("content")
        if token:
            return token.strip()

    match = _CSRF_RE.search(html)
    if match:
        return match.group(1).strip()
    return None


def fetch_csrf_token(client: GoodreadsClient, path: str = "/") -> str | None:
    html = client.get_text(path)
    return extract_csrf_token(html)
