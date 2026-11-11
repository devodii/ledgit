import tomllib
from typing import Any, ClassVar

from pydantic import BaseModel, Field

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.errors import ConnectorError
from receipts.connectors.http import HttpClient


class TomlCurrency(BaseModel):
    code: str = ""
    issuer: str = ""
    contract: str = ""


class StellarToml(BaseModel):
    domain: str
    reachable: bool
    accounts: list[str] = Field(default_factory=list)
    currencies: list[TomlCurrency] = Field(default_factory=list)
    endpoints: dict[str, str] = Field(default_factory=dict)
    url: str = ""
    org_names: list[str] = Field(default_factory=list)
    org_url: str = ""


SEP_KEYS = {
    "sep6": "TRANSFER_SERVER",
    "sep24": "TRANSFER_SERVER_SEP0024",
    "sep31": "DIRECT_PAYMENT_SERVER",
    "sep38": "ANCHOR_QUOTE_SERVER",
}


def parse_toml(domain: str, text: str, url: str) -> StellarToml:
    data: dict[str, Any] = tomllib.loads(text)
    docs = data.get("DOCUMENTATION") or {}
    return StellarToml(
        org_names=[str(docs[k]) for k in ("ORG_NAME", "ORG_DBA") if docs.get(k)],
        org_url=str(docs.get("ORG_URL", "")),
        domain=domain,
        reachable=True,
        url=url,
        accounts=[str(a) for a in data.get("ACCOUNTS", [])],
        currencies=[
            TomlCurrency(
                code=str(c.get("code", "")),
                issuer=str(c.get("issuer", "")),
                contract=str(c.get("contract", "")),
            )
            for c in data.get("CURRENCIES", [])
        ],
        endpoints={name: str(data[key]) for name, key in SEP_KEYS.items() if data.get(key)},
    )


class StellarTomlConnector(Connector):
    name: ClassVar[str] = "stellar_toml"
    allowed_domains: ClassVar[list[str]] = ["*"]
    rate_limit_rps: ClassVar[float] = 2.0
    emits: ClassVar[list[str]] = ["StellarToml"]

    def __init__(self) -> None:
        self.http = HttpClient(
            name=self.name, allowed_domains=[], rate_limit_rps=self.rate_limit_rps
        )

    def fetch(self, domain: str) -> StellarToml:
        domain = domain.strip().lower().removeprefix("https://").strip("/")
        url = f"https://{domain}/.well-known/stellar.toml"
        self.http.allowed_domains = [domain]
        try:
            response = self.http.get(url, cache_ttl=3600, retries=2)
        except ConnectorError:
            return StellarToml(domain=domain, reachable=False, url=url)
        if response.status != 200:
            return StellarToml(domain=domain, reachable=False, url=url)
        try:
            return parse_toml(domain, response.text, url)
        except tomllib.TOMLDecodeError:
            return StellarToml(domain=domain, reachable=False, url=url)

    def healthcheck(self) -> HealthResult:
        result = self.fetch("circle.com")
        return HealthResult(
            connector=self.name,
            ok=result.reachable,
            detail=f"{len(result.currencies)} currencies, endpoints={sorted(result.endpoints)}",
        )
