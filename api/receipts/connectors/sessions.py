from typing import ClassVar

from pydantic import BaseModel

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.http import HttpClient
from receipts.connectors.scf import strip_tags


class SessionPage(BaseModel):
    url: str
    text: str


class SessionsConnector(Connector):
    name: ClassVar[str] = "sessions"
    allowed_domains: ClassVar[list[str]] = ["meridian.stellar.org", "stellar.org"]
    rate_limit_rps: ClassVar[float] = 0.5
    emits: ClassVar[list[str]] = ["SessionPage"]

    def __init__(self) -> None:
        self.http = HttpClient(
            name=self.name,
            allowed_domains=self.allowed_domains,
            rate_limit_rps=self.rate_limit_rps,
            respect_robots=True,
        )

    def fetch(self, url: str) -> SessionPage:
        response = self.http.get(url, cache_ttl=86400)
        return SessionPage(url=url, text=strip_tags(response.text)[:20000])

    def healthcheck(self) -> HealthResult:
        try:
            page = self.fetch("https://meridian.stellar.org")
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(
            connector=self.name, ok=bool(page.text), detail=f"{len(page.text)} chars"
        )
