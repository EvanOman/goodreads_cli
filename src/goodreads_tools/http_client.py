from __future__ import annotations

import time
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://www.goodreads.com"
DEFAULT_USER_AGENT = "goodreads-tools/0.1 (+https://github.com/EvanOman/goodreads-tools)"


class GoodreadsClient:
    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        min_interval: float = 0.3,
        timeout: float = 20.0,
        cookies: dict[str, str] | None = None,
        max_retries: int = 2,
        retry_backoff: float = 0.5,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers={"User-Agent": DEFAULT_USER_AGENT},
            timeout=timeout,
            cookies=cookies,
        )
        self._min_interval = min_interval
        self._last_request = 0.0
        self._max_retries = max_retries
        self._retry_backoff = retry_backoff

    def _throttle(self) -> None:
        if self._min_interval <= 0:
            return
        now = time.monotonic()
        wait = self._min_interval - (now - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.monotonic()

    def get_json(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self._request("GET", path, params=params)
        return response.json()

    def get_text(self, path: str, params: dict[str, Any] | None = None) -> str:
        response = self._request("GET", path, params=params)
        return response.text

    def _request(
        self, method: str, path: str, params: dict[str, Any] | None = None
    ) -> httpx.Response:
        last_exc: Exception | None = None
        for attempt in range(self._max_retries + 1):
            self._throttle()
            try:
                response = self._client.request(method, path, params=params)
                response.raise_for_status()
                return response
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_exc = exc
                if attempt >= self._max_retries:
                    break
                time.sleep(self._retry_backoff * (2**attempt))
        if last_exc:
            raise last_exc
        raise RuntimeError("Request failed without an exception.")

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> GoodreadsClient:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
