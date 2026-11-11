import hashlib
import json
import threading
import time
from pathlib import Path
from typing import Any
from urllib import robotparser
from urllib.parse import urlparse

import httpx
from pydantic import BaseModel

from receipts.connectors.dns import install_doh_fallback
from receipts.connectors.errors import ConnectorError, DomainNotAllowed, RobotsDisallowed
from receipts.settings import get_settings

RETRY_STATUS = {429, 500, 502, 503, 504}


class CachedResponse(BaseModel):
    url: str
    status: int
    text: str
    from_cache: bool = False

    def data(self) -> Any:
        return json.loads(self.text)


class HttpClient:
    def __init__(
        self,
        *,
        name: str,
        allowed_domains: list[str],
        rate_limit_rps: float | None = None,
        cache_dir: Path | None = None,
        respect_robots: bool = False,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        settings = get_settings()
        if settings.dns_fallback:
            install_doh_fallback()
        self.name = name
        self.allowed_domains = allowed_domains
        self.min_interval = 1.0 / (rate_limit_rps or settings.http_rate_limit_rps)
        self.cache_dir = (cache_dir or settings.cache_dir) / "http" / name
        self.respect_robots = respect_robots
        self.user_agent = f"LedgitBot/0.1 (+{settings.http_contact_url})"
        self._client = httpx.Client(
            timeout=settings.http_timeout_seconds,
            headers={"User-Agent": self.user_agent},
            follow_redirects=True,
            transport=transport,
        )
        self._last_request = 0.0
        self._lock = threading.Lock()
        self._robots: dict[str, robotparser.RobotFileParser | None] = {}

    def _check_domain(self, url: str) -> str:
        host = urlparse(url).hostname or ""
        if not any(host == d or host.endswith("." + d) for d in self.allowed_domains):
            raise DomainNotAllowed(f"{host} is not in the {self.name} allowlist")
        return host

    def _check_robots(self, url: str, host: str) -> None:
        if host not in self._robots:
            parser = robotparser.RobotFileParser()
            try:
                response = self._client.get(f"https://{host}/robots.txt")
                if response.status_code == 200:
                    parser.parse(response.text.splitlines())
                    self._robots[host] = parser
                else:
                    self._robots[host] = None
            except httpx.HTTPError:
                self._robots[host] = None
        parser_or_none = self._robots[host]
        if parser_or_none and not parser_or_none.can_fetch(self.user_agent, url):
            raise RobotsDisallowed(f"robots.txt disallows {url}")

    def _cache_path(self, url: str, params: dict[str, Any] | None, body: Any) -> Path:
        key = json.dumps([url, params, body], sort_keys=True, default=str)
        digest = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / digest[:2] / f"{digest}.json"

    def _throttle(self) -> None:
        with self._lock:
            wait = self._last_request + self.min_interval - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._last_request = time.monotonic()

    def request(
        self,
        method: str,
        url: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: Any = None,
        headers: dict[str, str] | None = None,
        cache_ttl: float | None = None,
        retries: int = 3,
    ) -> CachedResponse:
        host = self._check_domain(url)
        path = self._cache_path(url, params, json_body)
        if (
            cache_ttl is not None
            and path.is_file()
            and time.time() - path.stat().st_mtime < cache_ttl
        ):
            cached = CachedResponse.model_validate_json(path.read_text())
            return cached.model_copy(update={"from_cache": True})
        if self.respect_robots:
            self._check_robots(url, host)
        last_error: Exception | None = None
        for attempt in range(retries):
            self._throttle()
            try:
                response = self._client.request(
                    method, url, params=params, json=json_body, headers=headers
                )
            except httpx.HTTPError as exc:
                last_error = exc
            else:
                if response.status_code not in RETRY_STATUS:
                    result = CachedResponse(
                        url=str(response.url), status=response.status_code, text=response.text
                    )
                    if cache_ttl is not None and response.status_code < 400:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(result.model_dump_json())
                    return result
                last_error = ConnectorError(f"{url} returned {response.status_code}")
            time.sleep(min(2**attempt, 8))
        raise ConnectorError(f"{url} failed after {retries} attempts: {last_error}")

    def get(self, url: str, **kwargs: Any) -> CachedResponse:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> CachedResponse:
        return self.request("POST", url, **kwargs)
