import re
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.http import HttpClient

BASE = "https://stellarlight.xyz"


class OnchainContract(BaseModel):
    address: str
    label: str = ""


ASSET_URL_RE = re.compile(r"/asset/([A-Za-z0-9]{1,12})-(G[A-Z2-7]{55})")
CONTRACT_URL_RE = re.compile(r"/contract/(C[A-Z2-7]{55})")


class ChainRef(BaseModel):
    kind: str
    ref: str
    source_url: str


def refs_from_url(url: str) -> list[ChainRef]:
    found = [
        ChainRef(kind="asset_issuer", ref=f"{c}-{i}", source_url=url)
        for c, i in ASSET_URL_RE.findall(url)
    ]
    found += [
        ChainRef(kind="soroban_contract", ref=c, source_url=url)
        for c in CONTRACT_URL_RE.findall(url)
    ]
    return found


class StellarLightProject(BaseModel):
    slug: str
    name: str
    category: str = ""
    status: str = ""
    status_source_url: str = ""
    asset_code: str = ""
    asset_issuer: str = ""
    contracts: list[OnchainContract] = Field(default_factory=list)
    scf_awarded: bool = False
    scf_total_usd: float | None = None
    scf_source_url: str = ""
    page_url: str = ""
    website: str = ""
    refs: list[ChainRef] = Field(default_factory=list)


class StellarLightConnector(Connector):
    name: ClassVar[str] = "stellarlight"
    allowed_domains: ClassVar[list[str]] = ["stellarlight.xyz"]
    rate_limit_rps: ClassVar[float] = 1.0
    emits: ClassVar[list[str]] = ["StellarLightProject"]

    def __init__(self) -> None:
        self.http = HttpClient(
            name=self.name, allowed_domains=self.allowed_domains, rate_limit_rps=self.rate_limit_rps
        )

    @staticmethod
    def _project(raw: dict[str, Any]) -> StellarLightProject:
        onchain = raw.get("onchain") or {}
        refs: list[ChainRef] = []
        for url in (
            (raw.get("deployment") or {}).get("sourceUrl"),
            raw.get("statusSourceUrl"),
        ):
            if url:
                refs.extend(refs_from_url(str(url)))
        return StellarLightProject(
            refs=refs,
            slug=raw["slug"],
            name=raw.get("name", ""),
            category=raw.get("category") or "",
            status=raw.get("status") or "",
            status_source_url=raw.get("statusSourceUrl") or "",
            asset_code=onchain.get("assetCode") or "",
            asset_issuer=onchain.get("issuer") or "",
            contracts=[
                OnchainContract(address=c["address"], label=c.get("label", ""))
                for c in (onchain.get("contracts") or [])
                if c.get("address")
            ],
            scf_awarded=bool(raw.get("scfAwarded")),
            scf_total_usd=raw.get("scfTotalAwardedUSD"),
            scf_source_url=raw.get("scfSourceUrl") or "",
            page_url=f"{BASE}/directory",
            website=str((raw.get("links") or {}).get("website") or ""),
        )

    def search_projects(self, query: str, limit: int = 10) -> list[StellarLightProject]:
        response = self.http.get(
            f"{BASE}/api/projects/search",
            params={"q": query, "limit": limit},
            cache_ttl=86400,
        )
        if response.status != 200:
            return []
        return [self._project(p) for p in response.data().get("projects", [])]

    def healthcheck(self) -> HealthResult:
        try:
            projects = self.search_projects("blend", limit=2)
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(
            connector=self.name, ok=bool(projects), detail=f"{len(projects)} projects"
        )
