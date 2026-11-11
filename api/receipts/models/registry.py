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


class EventSeed(BaseModel):
    model_config = ConfigDict(extra="allow")

    slug: str
    name: str
    location: str
    window: EventWindow
    discovery: dict[str, object] = Field(default_factory=dict)
    limits: dict[str, int] = Field(default_factory=dict)


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
