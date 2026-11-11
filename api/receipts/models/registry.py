import re
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from receipts.models.enums import CaptionSource, ClaimType, EvidenceKind, Network


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EventWindow(StrictModel):
    start: date
    end: date


class Discovery(BaseModel):
    playlists: list[str] = Field(default_factory=list)
    title_must_match: list[str] = Field(default_factory=list)
    published_after: date | None = None
    published_before: date | None = None
    session_pages: list[str] = Field(default_factory=list)


class Limits(BaseModel):
    max_videos: int = 80
    max_claims_per_talk: int = 5
    target_claims: int = 40


class EventSeed(BaseModel):
    slug: str
    name: str
    location: str
    window: EventWindow
    discovery: Discovery = Field(default_factory=Discovery)
    limits: Limits = Field(default_factory=Limits)


class Speaker(StrictModel):
    name: str = ""
    role: str = ""


class SourceRef(StrictModel):
    name: str
    url: str
    retrieved_at: datetime
    provides: list[str] = Field(default_factory=list)


class OrgRef(StrictModel):
    name: str
    domain: str = ""
    country: str = ""
    domain_source: str = ""
    country_source: str = ""

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")


class VideoRef(StrictModel):
    id: str
    url_at_timestamp: str
    start_seconds: int = Field(ge=0)


class ClaimBody(StrictModel):
    type: ClaimType
    quote: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    speaker: Speaker
    org: OrgRef
    video: VideoRef
    caption_source: CaptionSource


class Scf(StrictModel):
    found: bool = False
    project_url: str = ""
    awarded_usd: Decimal | None = None
    source: str = ""


class Backing(StrictModel):
    scf: Scf = Field(default_factory=Scf)


class EvidenceItem(StrictModel):
    kind: EvidenceKind
    network: Network
    ref: str = Field(min_length=1)
    found_via: str = Field(min_length=1)


class Provenance(StrictModel):
    extractor_model: str
    extracted_at: datetime
    confidence: float = Field(ge=0, le=1)
    transcript_sha256: str

    @field_validator("transcript_sha256")
    @classmethod
    def _hex(cls, value: str) -> str:
        if value and not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("transcript_sha256 must be a 64 character lowercase hex digest")
        return value


class RegistryEntry(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    event: str
    claim: ClaimBody
    backing: Backing = Field(default_factory=Backing)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    sources: list[SourceRef] = Field(default_factory=list)
    provenance: Provenance


class OrgCorrection(StrictModel):
    domain: str | None = None
    country: str | None = None


class EvidenceKey(StrictModel):
    kind: EvidenceKind
    network: Network
    ref: str


class Correction(StrictModel):
    claim_id: str
    source_url: str = Field(pattern=r"^https?://")
    note: str = ""
    org: OrgCorrection | None = None
    add_evidence: list[EvidenceItem] = Field(default_factory=list)
    remove_evidence: list[EvidenceKey] = Field(default_factory=list)
