import re
from typing import ClassVar

from pydantic import BaseModel

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.errors import ConnectorError
from receipts.connectors.http import HttpClient
from receipts.models.enums import Network
from receipts.settings import get_settings


class AssetStats(BaseModel):
    found: bool
    code: str
    issuer: str
    holders: int = 0
    supply: float = 0.0
    network: Network = Network.pubnet


class AccountInfo(BaseModel):
    found: bool
    address: str
    network: Network = Network.pubnet


class HorizonConnector(Connector):
    name: ClassVar[str] = "horizon"
    allowed_domains: ClassVar[list[str]] = [
        "horizon.stellar.lobstr.co",
        "horizon-testnet.stellar.org",
        "horizon.stellar.org",
    ]
    rate_limit_rps: ClassVar[float] = 5.0
    emits: ClassVar[list[str]] = ["AssetStats", "AccountInfo"]

    def __init__(self) -> None:
        settings = get_settings()
        self.urls = {
            Network.pubnet: settings.horizon_url.rstrip("/"),
            Network.testnet: settings.horizon_testnet_url.rstrip("/"),
        }
        self.http = HttpClient(
            name=self.name, allowed_domains=self.allowed_domains, rate_limit_rps=self.rate_limit_rps
        )

    def asset(self, code: str, issuer: str, network: Network = Network.pubnet) -> AssetStats:
        response = self.http.get(
            f"{self.urls[network]}/assets",
            params={"asset_code": code, "asset_issuer": issuer, "limit": 1},
            cache_ttl=600,
        )
        if response.status != 200:
            raise ConnectorError(f"horizon assets returned {response.status}")
        records = response.data().get("_embedded", {}).get("records", [])
        if not records:
            return AssetStats(found=False, code=code, issuer=issuer, network=network)
        record = records[0]
        accounts = record.get("accounts", {})
        return AssetStats(
            found=True,
            code=code,
            issuer=issuer,
            network=network,
            holders=int(accounts.get("authorized", 0)) + int(record.get("num_contracts", 0)),
            supply=float(record.get("balances", {}).get("authorized", 0))
            + float(record.get("contracts_amount", 0))
            + float(record.get("liquidity_pools_amount", 0)),
        )

    def issued_assets(self, issuer: str, network: Network = Network.pubnet) -> list[AssetStats]:
        response = self.http.get(
            f"{self.urls[network]}/assets",
            params={"asset_issuer": issuer, "limit": 20},
            cache_ttl=600,
        )
        if response.status != 200:
            return []
        out: list[AssetStats] = []
        for record in response.data().get("_embedded", {}).get("records", []):
            out.append(
                AssetStats(
                    found=True,
                    code=record["asset_code"],
                    issuer=issuer,
                    network=network,
                    holders=int(record.get("accounts", {}).get("authorized", 0))
                    + int(record.get("num_contracts", 0)),
                    supply=float(record.get("balances", {}).get("authorized", 0)),
                )
            )
        return out

    def assets_by_code(self, code: str, limit: int = 60) -> list[AssetStats]:
        response = self.http.get(
            f"{self.urls[Network.pubnet]}/assets",
            params={"asset_code": code, "limit": limit},
            cache_ttl=3600,
        )
        if response.status != 200:
            return []
        out: list[AssetStats] = []
        for record in response.data().get("_embedded", {}).get("records", []):
            if record.get("asset_code") != code:
                continue
            out.append(
                AssetStats(
                    found=True,
                    code=code,
                    issuer=record["asset_issuer"],
                    holders=int(record.get("accounts", {}).get("authorized", 0))
                    + int(record.get("num_contracts", 0)),
                    supply=float(record.get("balances", {}).get("authorized", 0)),
                )
            )
        return out

    def home_domain(self, address: str) -> str:
        response = self.http.get(f"{self.urls[Network.pubnet]}/accounts/{address}", cache_ttl=86400)
        if response.status != 200:
            return ""
        return str(response.data().get("home_domain") or "").lower()

    def core_version(self, network: Network) -> tuple[int, ...]:
        info = self.http.get(self.urls[network] + "/").data()
        match = re.search(r"(\d+(?:\.\d+)+)", str(info.get("core_version", "")))
        return tuple(int(p) for p in match.group(1).split(".")) if match else ()

    def account(self, address: str, network: Network = Network.pubnet) -> AccountInfo:
        response = self.http.get(f"{self.urls[network]}/accounts/{address}", cache_ttl=600)
        if response.status == 404:
            return AccountInfo(found=False, address=address, network=network)
        if response.status != 200:
            raise ConnectorError(f"horizon accounts returned {response.status}")
        return AccountInfo(found=True, address=address, network=network)

    def healthcheck(self) -> HealthResult:
        try:
            response = self.http.get(self.urls[Network.pubnet] + "/")
            ledger = response.data().get("history_latest_ledger")
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        return HealthResult(connector=self.name, ok=bool(ledger), detail=f"ledger {ledger}")
