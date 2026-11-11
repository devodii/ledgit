from pydantic import BaseModel

from receipts.models.enums import ClaimType, ObservationResult, VerdictStatus


class EvidenceResult(BaseModel):
    label: str
    result: ObservationResult
    summary: str


def compute_verdict(
    claim_type: ClaimType,
    age_days: int | None,
    results: list[EvidenceResult],
    previous: VerdictStatus | None,
    pending_days: int,
) -> tuple[VerdictStatus, str]:
    if claim_type == ClaimType.open_ask:
        return VerdictStatus.open_ask, "Requested on stage, no builder identified."
    if (
        age_days is not None
        and age_days < pending_days
        and not any(r.result == ObservationResult.live for r in results)
    ):
        return (
            VerdictStatus.pending,
            f"The talk was given {age_days} days ago, too recent to assess.",
        )
    if not results:
        return (
            VerdictStatus.no_trace_found,
            "No on-chain or public reference could be linked to this organisation yet.",
        )
    ok = [r for r in results if r.result != ObservationResult.error]
    if not ok:
        reason = "Every check failed to run, so the previous verdict is kept."
        return previous or VerdictStatus.pending, reason
    lines = "; ".join(f"{r.label}: {r.summary}" for r in results)
    live = [r for r in ok if r.result == ObservationResult.live]
    if live:
        return VerdictStatus.live, f"{len(live)} of {len(results)} checks found live. {lines}."
    if any(r.result == ObservationResult.testnet_only for r in ok):
        return VerdictStatus.testnet_only, f"Found on testnet, not on mainnet. {lines}."
    if any(r.result == ObservationResult.inactive for r in ok):
        return (
            VerdictStatus.pending,
            f"Present on mainnet but activity could not be confirmed yet. {lines}.",
        )
    return VerdictStatus.no_trace_found, f"None of the checks found a trace. {lines}."
