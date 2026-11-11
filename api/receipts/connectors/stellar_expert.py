from typing import ClassVar

from pydantic import BaseModel

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.http import HttpClient
from receipts.settings import get_settings


class DirectoryEntry(BaseModel):
    address: str
    name: str = ""
    domain: str = ""
    tags: list[str] = []


class StellarExpertConnector(Connector):
    name: ClassVar[str] = "stellar_expert"
    allowed_domains: ClassVar[list[str]] = ["api.stellar.expert"]
    rate_limit_rps: ClassVar[float] = 1.0
    emits: ClassVar[list[str]] = ["DirectoryEntry"]

    def __init__(self) -> None:
        self.base = get_settings().stellar_expert_url.rstrip("/")
        self.http = HttpClient(
            name=self.name, allowed_domains=self.allowed_domains, rate_limit_rps=self.rate_limit_rps
        )

    def search_directory(self, query: str, limit: int = 10) -> list[DirectoryEntry]:
        response = self.http.get(
            f"{self.base}/explorer/directory",
            params={"search": query, "limit": limit},
            cache_ttl=86400,
        )
        if response.status != 200:
            return []
        records = response.data().get("_embedded", {}).get("records", [])
        return [
            DirectoryEntry(
                address=r.get("address", ""),
                name=r.get("name", ""),
                domain=r.get("domain", ""),
                tags=r.get("tags", []),
            )
            for r in records
            if r.get("address")
        ]

    def healthcheck(self) -> HealthResult:
        try:
            entries = self.search_directory("circle", limit=3)
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(connector=self.name, ok=bool(entries), detail=f"{len(entries)} entries")
