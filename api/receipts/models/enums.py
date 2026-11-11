from enum import StrEnum


class ClaimType(StrEnum):
    partner_launch = "partner_launch"
    roadmap = "roadmap"
    protocol_feature = "protocol_feature"
    open_ask = "open_ask"


class VerdictStatus(StrEnum):
    live = "live"
    testnet_only = "testnet_only"
    no_trace_found = "no_trace_found"
    pending = "pending"
    open_ask = "open_ask"


class EvidenceKind(StrEnum):
    asset_issuer = "asset_issuer"
    soroban_contract = "soroban_contract"
    anchor = "anchor"
    protocol_upgrade = "protocol_upgrade"


class Network(StrEnum):
    pubnet = "pubnet"
    testnet = "testnet"


class CaptionSource(StrEnum):
    manual = "manual"
    auto = "auto"


class ObservationResult(StrEnum):
    live = "live"
    testnet_only = "testnet_only"
    not_found = "not_found"
    error = "error"
