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
    extractor_model: str
    extracted_at: datetime
