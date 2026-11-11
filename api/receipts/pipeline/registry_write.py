import hashlib
import json

import yaml
from pydantic import TypeAdapter

from receipts.db.connection import connect
from receipts.models.enums import CaptionSource, EvidenceKind, Network
from receipts.models.pipeline import Candidate, OrgResolution
from receipts.models.registry import (
    Backing,
    ClaimBody,
    EventSeed,
    EvidenceItem,
    OrgRef,
    Provenance,
    RegistryEntry,
    Scf,
    SourceRef,
    Speaker,
    VideoRef,
)
from receipts.pipeline.common import stage_cache, write_report
from receipts.registry.loader import sync_event, sync_registry
from receipts.settings import get_settings

_entries = TypeAdapter(list[RegistryEntry])


def claim_id(candidate: Candidate) -> str:
    digest = hashlib.sha256(f"{candidate.video_id}|{candidate.quote}".encode()).hexdigest()[:6]
    return f"{OrgRef(name=candidate.org_name).slug}-{digest}"


def build_entry(event: str, candidate: Candidate, org: OrgResolution) -> RegistryEntry:
    evidence = [
        EvidenceItem(
            kind=EvidenceKind(e.kind), network=Network(e.network), ref=e.ref, found_via=e.found_via
        )
        for e in org.evidence
    ]
    sources = [SourceRef.model_validate(s.model_dump()) for s in org.sources]
    if candidate.protocol_version:
        evidence.append(
            EvidenceItem(
                kind=EvidenceKind.protocol_upgrade,
                network=Network.pubnet,
                ref=f"protocol-{candidate.protocol_version}",
                found_via=(
                    f"named in the talk, video {candidate.video_id} at {candidate.start_seconds}s"
                ),
            )
        )
    video_url = f"https://www.youtube.com/watch?v={candidate.video_id}&t={candidate.start_seconds}s"
    return RegistryEntry(
        id=claim_id(candidate),
        event=event,
        claim=ClaimBody(
            type=candidate.claim_type,
            quote=candidate.quote,
            summary=candidate.summary,
            speaker=Speaker(name=candidate.speaker_name, role=candidate.speaker_role),
            org=OrgRef(
                name=candidate.org_name,
                domain=org.domain,
                country=org.country,
                domain_source=org.domain_source,
                country_source=org.country_source,
            ),
            video=VideoRef(
                id=candidate.video_id,
                url_at_timestamp=video_url,
                start_seconds=candidate.start_seconds,
            ),
            caption_source=CaptionSource(candidate.caption_source),
        ),
        backing=Backing(
            scf=Scf(
                found=org.scf_found,
                project_url=org.scf_project_url,
                awarded_usd=org.scf_awarded_usd,
                source=org.scf_source,
            )
        ),
        evidence=evidence,
        sources=sources,
        provenance=Provenance(
            extractor_model=candidate.extractor_model,
            extracted_at=candidate.extracted_at,
            confidence=candidate.score,
            transcript_sha256=candidate.transcript_sha256,
        ),
    )


def dump(entries: list[RegistryEntry]) -> str:
    data = _entries.dump_python(entries, mode="json")
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=1000)


def run_write(seed: EventSeed) -> int:
    settings = get_settings()
    ranked = [
        Candidate.model_validate(c)
        for c in json.loads((stage_cache("ranked") / f"{seed.slug}.json").read_text())
    ]
    public: list[RegistryEntry] = []
    review: list[RegistryEntry] = []
    drops: dict[str, int] = {}
    for candidate in ranked:
        resolution_path = stage_cache("resolve") / f"{OrgRef(name=candidate.org_name).slug}.json"
        org = OrgResolution.model_validate_json(resolution_path.read_text())
        entry = build_entry(seed.slug, candidate, org)
        if entry.provenance.confidence < settings.pipeline_min_confidence:
            review.append(entry)
            drops["low_confidence"] = drops.get("low_confidence", 0) + 1
        else:
            public.append(entry)
    public.sort(key=lambda e: e.id)
    review.sort(key=lambda e: e.id)
    for folder, entries in (("registry", public), ("review", review)):
        target = settings.data_dir / folder
        target.mkdir(parents=True, exist_ok=True)
        (target / f"{seed.slug}.yaml").write_text(dump(entries))
    with connect() as conn:
        sync_event(conn, seed)
        sync_registry(conn, public)
        conn.commit()
    write_report(
        "write", seed.slug, len(ranked), len(public), drops, [f"review items: {len(review)}"]
    )
    return len(public)
