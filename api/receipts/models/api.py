from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel

from receipts.models.enums import (
    CaptionSource,
    ClaimType,
    EvidenceKind,
    Network,
    ObservationResult,
    VerdictStatus,
)


class Health(BaseModel):
    status: str


class OrgSummary(BaseModel):
    slug: str
    name: str
    domain: str
    country: str
    claim_count: int


class ClaimSummary(BaseModel):
    id: str
    event: str
    claim_type: ClaimType
    status: VerdictStatus
    quote: str
    summary: str
    speaker_name: str
    speaker_role: str
    org_slug: str
    org_name: str
    org_country: str
    video_url: str
    last_checked_at: datetime | None


class ClaimPage(BaseModel):
    items: list[ClaimSummary]
    next_cursor: str | None


class ObservationOut(BaseModel):
    checked_at: datetime
    result: ObservationResult
    detail: dict[str, Any]


class EvidenceOut(BaseModel):
    id: int
    kind: EvidenceKind
    network: Network
    ref: str
    found_via: str
    latest_observation: ObservationOut | None


class VerdictChangeOut(BaseModel):
    claim_id: str
    from_status: VerdictStatus | None
    to_status: VerdictStatus
    reason: str
    changed_at: datetime


class VerdictOut(BaseModel):
    status: VerdictStatus
    reason: str
    checked_at: datetime | None


class VideoOut(BaseModel):
    id: str
    url: str
    start_seconds: int
    caption_source: CaptionSource


class ScfOut(BaseModel):
    found: bool
    project_url: str
    awarded_usd: Decimal | None


class OrgOut(BaseModel):
    slug: str
    name: str
    domain: str
    country: str


class SourceOut(BaseModel):
    name: str
    url: str
    retrieved_at: datetime
    provides: list[str]


class ClaimDetail(BaseModel):
    id: str
    event: str
    claim_type: ClaimType
    quote: str
    summary: str
    speaker_name: str
    speaker_role: str
    org: OrgOut
    video: VideoOut
    scf: ScfOut
    evidence: list[EvidenceOut]
    verdict: VerdictOut
    history: list[VerdictChangeOut]
    extractor_model: str
    confidence: float
    sources: list[SourceOut]
    domain_source: str
    country_source: str
    scf_source: str
    transcript_sha256: str


class OrgDetail(BaseModel):
    org: OrgOut
    claims: list[ClaimSummary]


class StatusCount(BaseModel):
    status: VerdictStatus
    count: int


class TypeCount(BaseModel):
    claim_type: ClaimType
    count: int


class EventSummary(BaseModel):
    slug: str
    name: str
    location: str
    window_start: date
    window_end: date
    total: int
    by_status: list[StatusCount]
    by_type: list[TypeCount]


class ChangeItem(BaseModel):
    id: int
    claim_id: str
    org_name: str
    summary: str
    from_status: VerdictStatus | None
    to_status: VerdictStatus
    reason: str
    changed_at: datetime


class ChangePage(BaseModel):
    items: list[ChangeItem]
    next_cursor: str | None


class Meta(BaseModel):
    last_verified_at: datetime | None
    data_version: str


class HumanTask(BaseModel):
    id: int
    kind: str
    description: str
    url: str
    resume_hint: str
    created_at: datetime


class TaskList(BaseModel):
    open_count: int
    tasks: list[HumanTask]
