import re

from pydantic import BaseModel, Field

from receipts.connectors.errors import ConnectorError
from receipts.connectors.horizon import HorizonConnector
from receipts.connectors.sep_info import SepInfoConnector
from receipts.connectors.soroban import SorobanConnector
from receipts.connectors.stellar_toml import StellarTomlConnector
from receipts.models.enums import EvidenceKind, Network, ObservationResult
from receipts.settings import get_settings

ACCOUNT_RE = re.compile(r"^G[A-Z2-7]{55}$")


class Observation(BaseModel):
    result: ObservationResult
    summary: str
    detail: dict[str, object] = Field(default_factory=dict)


def check_asset_issuer(ref: str, horizon: HorizonConnector) -> Observation:
    settings = get_settings()
    code, _, issuer = ref.partition("-")
    if not issuer:
        code, issuer = "", ref
    if not ACCOUNT_RE.match(issuer):
        return Observation(result=ObservationResult.error, summary=f"{ref} is not a valid asset")
    for network in (Network.pubnet, Network.testnet):
        assets = (
            [horizon.asset(code, issuer, network)]
            if code
            else horizon.issued_assets(issuer, network)
        )
        found = [a for a in assets if a.found and a.supply > 0]
        qualifying = [a for a in found if a.holders >= settings.verify_min_asset_holders]
        if network == Network.pubnet and qualifying:
            top = max(qualifying, key=lambda a: a.holders)
            return Observation(
                result=ObservationResult.live,
                summary=f"{top.code} on mainnet with {top.holders:,} holders",
                detail={"asset": top.code, "holders": top.holders, "supply": top.supply},
            )
        if network == Network.pubnet and found:
            top = max(found, key=lambda a: a.holders)
            return Observation(
                result=ObservationResult.inactive,
                summary=f"{top.code} exists on mainnet with {top.holders} holders, below the "
                f"minimum of {settings.verify_min_asset_holders}",
                detail={"asset": top.code, "holders": top.holders},
            )
        if network == Network.testnet and found:
            return Observation(
                result=ObservationResult.testnet_only,
                summary=f"{found[0].code} found on testnet, not on mainnet",
                detail={"asset": found[0].code, "holders": found[0].holders},
            )
    return Observation(
        result=ObservationResult.not_found, summary="asset not found on either network"
    )


def check_soroban_contract(ref: str, soroban: SorobanConnector) -> Observation:
    days = get_settings().verify_contract_activity_days
    main = soroban.contract(ref, Network.pubnet, days)
    if main.exists and main.recent_events > 0:
        return Observation(
            result=ObservationResult.live,
            summary=(
                f"deployed on mainnet with invocations in the last {main.retention_days:g} days"
            ),
            detail={"events": main.recent_events, "window_days": main.retention_days},
        )
    if main.exists:
        return Observation(
            result=ObservationResult.inactive,
            summary="deployed on mainnet, no invocations in the available history "
            f"({main.retention_days:g} days)",
            detail={"events": 0, "window_days": main.retention_days},
        )
    test = soroban.contract(ref, Network.testnet, days)
    if test.exists:
        return Observation(
            result=ObservationResult.testnet_only,
            summary="deployed on testnet, not on mainnet",
            detail={"events": test.recent_events},
        )
    return Observation(
        result=ObservationResult.not_found, summary="contract not found on either network"
    )


def check_anchor(ref: str, toml: StellarTomlConnector, sep: SepInfoConnector) -> Observation:
    record = toml.fetch(ref)
    if not record.reachable:
        return Observation(result=ObservationResult.not_found, summary="stellar.toml not reachable")
    probes = sep.probe(record)
    up = [p.sep for p in probes if p.responded]
    if up:
        return Observation(
            result=ObservationResult.live,
            summary=f"stellar.toml reachable, {', '.join(up)} responded",
            detail={"responding": up, "declared": [p.sep for p in probes]},
        )
    declared = [p.sep for p in probes]
    return Observation(
        result=ObservationResult.not_found,
        summary="stellar.toml reachable, "
        + (f"{', '.join(declared)} did not respond" if declared else "no SEP endpoints declared"),
        detail={"declared": declared},
    )


def check_protocol(ref: str, soroban: SorobanConnector) -> Observation:
    match = re.fullmatch(r"protocol-(\d+)", ref)
    if not match:
        return Observation(result=ObservationResult.error, summary=f"unsupported reference {ref}")
    wanted = int(match.group(1))
    main = soroban.protocol_version(Network.pubnet)
    if main >= wanted:
        return Observation(
            result=ObservationResult.live,
            summary=f"mainnet is running protocol {main}, which includes protocol {wanted}",
            detail={"mainnet_protocol": main},
        )
    test = soroban.protocol_version(Network.testnet)
    if test >= wanted:
        return Observation(
            result=ObservationResult.testnet_only,
            summary=f"testnet is on protocol {test}, mainnet on {main}",
            detail={"mainnet_protocol": main, "testnet_protocol": test},
        )
    return Observation(
        result=ObservationResult.not_found, summary=f"neither network is on protocol {wanted} yet"
    )


class Checkers:
    def __init__(self) -> None:
        self.horizon = HorizonConnector()
        self.soroban = SorobanConnector()
        self.toml = StellarTomlConnector()
        self.sep = SepInfoConnector()

    def run(self, kind: str, ref: str) -> Observation:
        try:
            match EvidenceKind(kind):
                case EvidenceKind.asset_issuer:
                    return check_asset_issuer(ref, self.horizon)
                case EvidenceKind.soroban_contract:
                    return check_soroban_contract(ref, self.soroban)
                case EvidenceKind.anchor:
                    return check_anchor(ref, self.toml, self.sep)
                case EvidenceKind.protocol_upgrade:
                    return check_protocol(ref, self.soroban)
        except ConnectorError as exc:
            return Observation(result=ObservationResult.error, summary=f"check failed: {exc}"[:200])
        return Observation(result=ObservationResult.error, summary="unknown evidence kind")
