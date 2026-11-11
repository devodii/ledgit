from typing import Any, ClassVar

from pydantic import BaseModel
from stellar_sdk import Address, xdr

from receipts.connectors.base import Connector, HealthResult
from receipts.connectors.errors import ConnectorError
from receipts.connectors.http import HttpClient
from receipts.models.enums import Network
from receipts.settings import get_settings


class ContractStatus(BaseModel):
    exists: bool
    contract_id: str
    network: Network
    recent_events: int = 0
    window_ledgers: int = 0
    retention_days: float = 0.0


def instance_key(contract_id: str) -> str:
    key = xdr.LedgerKey(
        type=xdr.LedgerEntryType.CONTRACT_DATA,
        contract_data=xdr.LedgerKeyContractData(
            contract=Address(contract_id).to_xdr_sc_address(),
            key=xdr.SCVal(xdr.SCValType.SCV_LEDGER_KEY_CONTRACT_INSTANCE),
            durability=xdr.ContractDataDurability.PERSISTENT,
        ),
    )
    return key.to_xdr()


class SorobanConnector(Connector):
    name: ClassVar[str] = "soroban"
    allowed_domains: ClassVar[list[str]] = ["mainnet.sorobanrpc.com", "soroban-testnet.stellar.org"]
    rate_limit_rps: ClassVar[float] = 3.0
    emits: ClassVar[list[str]] = ["ContractStatus"]
    LEDGERS_PER_DAY = 17280

    def __init__(self) -> None:
        settings = get_settings()
        self.urls = {
            Network.pubnet: settings.soroban_rpc_url,
            Network.testnet: settings.soroban_rpc_testnet_url,
        }
        self.http = HttpClient(
            name=self.name, allowed_domains=self.allowed_domains, rate_limit_rps=self.rate_limit_rps
        )

    def _rpc(self, network: Network, method: str, params: dict[str, Any] | None = None) -> Any:
        response = self.http.post(
            self.urls[network],
            json_body={"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}},
        )
        body = response.data()
        if "error" in body:
            raise ConnectorError(f"{method}: {body['error']}")
        return body["result"]

    def contract(self, contract_id: str, network: Network, activity_days: int) -> ContractStatus:
        entries = self._rpc(network, "getLedgerEntries", {"keys": [instance_key(contract_id)]}).get(
            "entries"
        )
        if not entries:
            return ContractStatus(exists=False, contract_id=contract_id, network=network)
        health = self._rpc(network, "getHealth")
        latest, oldest = health["latestLedger"], health["oldestLedger"]
        retention_days = (latest - oldest) / self.LEDGERS_PER_DAY
        window = min(activity_days * self.LEDGERS_PER_DAY, latest - oldest)
        events = self._rpc(
            network,
            "getEvents",
            {
                "startLedger": latest - window,
                "filters": [{"type": "contract", "contractIds": [contract_id]}],
                "pagination": {"limit": 100},
            },
        )
        return ContractStatus(
            exists=True,
            contract_id=contract_id,
            network=network,
            recent_events=len(events.get("events", [])),
            window_ledgers=window,
            retention_days=round(retention_days, 1),
        )

    def healthcheck(self) -> HealthResult:
        try:
            health = self._rpc(Network.pubnet, "getHealth")
        except Exception as exc:
            return HealthResult(connector=self.name, ok=False, detail=str(exc)[:200])
        days = (health["latestLedger"] - health["oldestLedger"]) / self.LEDGERS_PER_DAY
        return HealthResult(
            connector=self.name,
            ok=health["status"] == "healthy",
            detail=f"retention about {days:.1f} days",
        )
