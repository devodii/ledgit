from datetime import datetime

from pydantic import BaseModel, Field

from receipts.models.enums import CaptionSource, ClaimType


class StageReport(BaseModel):
    stage: str
    event: str
    counts_in: int
    counts_out: int
    drops: dict[str, int] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    finished_at: datetime


class RawClaim(BaseModel):
    quote: str
    summary: str
    claim_type: ClaimType
    speaker_name: str = ""
    speaker_role: str = ""
    org_name: str = ""
    org_domain: str = ""
    protocol_version: int | None = None
    specificity: float = Field(default=0, ge=0, le=1)
    verifiability: float = Field(default=0, ge=0, le=1)


class RawClaimBatch(BaseModel):
    claims: list[RawClaim] = Field(default_factory=list)


class Candidate(BaseModel):
    video_id: str
    video_title: str
    quote: str
    summary: str
    claim_type: ClaimType
    speaker_name: str
    speaker_role: str
    org_name: str
    org_domain: str
    protocol_version: int | None
    start_seconds: int
    caption_source: CaptionSource
    transcript_sha256: str
    specificity: float
    verifiability: float
    score: float = 0.0
    judge_confidence: float | None = None
    judge_issue: str = ""
    judge_reason: str = ""
    extractor_model: str
    extracted_at: datetime


class OrgResolution(BaseModel):
    org_name: str
    slug: str
    domain: str = ""
    domain_source: str = ""
    country: str = ""
    country_source: str = ""
    scf_found: bool = False
    scf_project_url: str = ""
    scf_awarded_usd: float | None = None
    scf_source: str = ""
    evidence: list["EvidenceDraft"] = Field(default_factory=list)
    sources: list["SourceDraft"] = Field(default_factory=list)


class EvidenceDraft(BaseModel):
    kind: str
    network: str = "pubnet"
    ref: str
    found_via: str


class SourceDraft(BaseModel):
    name: str
    url: str
    retrieved_at: datetime
    provides: list[str] = Field(default_factory=list)


OrgResolution.model_rebuild()


class JudgeVerdict(BaseModel):
    index: int
    checkable: bool
    summary_faithful: bool
    org_correct: bool
    type_correct: bool
    speaker_correct: bool | None = None
    confidence: float = Field(ge=0, le=1)
    issue: str = ""


class JudgeBatch(BaseModel):
    verdicts: list[JudgeVerdict] = Field(default_factory=list)
