from __future__ import annotations

import json
import time
from collections.abc import Iterable
from dataclasses import dataclass
from http.cookies import SimpleCookie
from pathlib import Path

import browser_cookie3

CONFIG_DIR = Path.home() / ".config" / "goodreads-tools"
SESSION_PATH = CONFIG_DIR / "session.json"


@dataclass(frozen=True)
class SessionData:
    cookies: dict[str, str]
    source: str
    created_at: float


def parse_cookie_string(cookie_string: str) -> dict[str, str]:
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    return {key: morsel.value for key, morsel in cookie.items()}


def _cookies_from_jar(jar: Iterable) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for item in jar:
        domain = getattr(item, "domain", "") or ""
        if "goodreads.com" not in domain:
            continue
        cookies[item.name] = item.value
    return cookies


def load_cookies_from_browser(browser: str | None = None) -> dict[str, str]:
    if browser:
        loader = getattr(browser_cookie3, browser, None)
        if loader is None:
            raise ValueError(f"Unsupported browser: {browser}")
        jar = loader(domain_name="goodreads.com")
    else:
        jar = browser_cookie3.load(domain_name="goodreads.com")
    cookies = _cookies_from_jar(jar)
    if not cookies:
        raise ValueError("No Goodreads cookies found in browser store.")
    return cookies


def save_session(session: SessionData, path: Path = SESSION_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "cookies": session.cookies,
        "source": session.source,
        "created_at": session.created_at,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_session(path: Path = SESSION_PATH) -> SessionData:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SessionData(
        cookies=payload.get("cookies", {}),
        source=payload.get("source", "unknown"),
        created_at=payload.get("created_at", 0.0),
    )


def create_session_from_cookie_string(cookie_string: str) -> SessionData:
    cookies = parse_cookie_string(cookie_string)
    if not cookies:
        raise ValueError("Cookie string is empty or invalid.")
    return SessionData(cookies=cookies, source="cookie-string", created_at=time.time())


def create_session_from_browser(browser: str | None = None) -> SessionData:
    cookies = load_cookies_from_browser(browser)
    source = browser or "auto"
    return SessionData(cookies=cookies, source=source, created_at=time.time())
