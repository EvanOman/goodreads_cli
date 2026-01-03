from __future__ import annotations

import json
import re
from typing import Any

from goodreads_cli.http_client import GoodreadsClient
from goodreads_cli.models import UserInfo

_CURRENT_USER_RE = re.compile(
    r"CurrentUserStore\.initializeWith\((\{.*?\})\);",
    re.DOTALL,
)


def parse_current_user(html: str) -> UserInfo | None:
    match = _CURRENT_USER_RE.search(html)
    if not match:
        return None
    payload = json.loads(match.group(1))
    current = payload.get("currentUser")
    if not current:
        return None
    return _build_user_info(current)


def _build_user_info(current: dict[str, Any]) -> UserInfo:
    user_id = current.get("id") or current.get("legacyId") or current.get("userId")
    name = current.get("name") or current.get("displayName")
    profile_url = current.get("profileUrl") or current.get("link") or current.get("webUrl")
    return UserInfo(
        user_id=str(user_id) if user_id is not None else "",
        name=name or "",
        profile_url=profile_url,
    )


def get_current_user(client: GoodreadsClient) -> UserInfo | None:
    html = client.get_text("/")
    return parse_current_user(html)
