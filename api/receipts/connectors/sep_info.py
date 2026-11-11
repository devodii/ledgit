from typing import ClassVar

from pydantic import BaseModel

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.errors import ConnectorError
from receipts.connectors.http import HttpClient
from receipts.connectors.stellar_toml import StellarToml


class SepProbe(BaseModel):
    sep: str
    url: str
    responded: bool
    status: int | None = None


class SepInfoConnector(Connector):
    name: ClassVar[str] = "sep_info"
    allowed_domains: ClassVar[list[str]] = ["*"]
    rate_limit_rps: ClassVar[float] = 2.0
    emits: ClassVar[list[str]] = ["SepProbe"]

    def __init__(self) -> None:
        self.http = HttpClient(
            name=self.name, allowed_domains=[], rate_limit_rps=self.rate_limit_rps
        )

    def probe(self, toml: StellarToml) -> list[SepProbe]:
        results: list[SepProbe] = []
        for sep, base in toml.endpoints.items():
            url = base.rstrip("/") + "/info"
            host = url.split("/")[2].split(":")[0]
            self.http.allowed_domains = [host]
            try:
                response = self.http.get(url, cache_ttl=600, retries=2)
                ok = response.status == 200
                results.append(SepProbe(sep=sep, url=url, responded=ok, status=response.status))
            except ConnectorError:
                results.append(SepProbe(sep=sep, url=url, responded=False))
        return results

    def healthcheck(self) -> HealthResult:
        from receipts.connectors.stellar_toml import StellarTomlConnector

        toml = StellarTomlConnector().fetch("circle.com")
        probes = self.probe(toml)
        return HealthResult(
            connector=self.name,
            ok=toml.reachable,
            detail=", ".join(f"{p.sep}={'up' if p.responded else 'down'}" for p in probes)
            or "no SEP endpoints declared",
        )
