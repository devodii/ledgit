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
    Correction,
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
from receipts.pipeline.resolve import valid_ref
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
        if valid_ref(e.kind, e.ref)
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


def apply_corrections(
    entries: list[RegistryEntry], corrections: list[Correction]
) -> list[RegistryEntry]:
    by_id = {e.id: e for e in entries}
    for correction in corrections:
        entry = by_id.get(correction.claim_id)
        if entry is None:
            continue
        label = f"correction {correction.source_url}"
        if correction.org:
            if correction.org.domain is not None:
                entry.claim.org.domain = correction.org.domain
                entry.claim.org.domain_source = label
            if correction.org.country is not None:
                entry.claim.org.country = correction.org.country
                entry.claim.org.country_source = label
        removed = {(k.kind, k.network, k.ref) for k in correction.remove_evidence}
        entry.evidence = [e for e in entry.evidence if (e.kind, e.network, e.ref) not in removed]
        known = {(e.kind, e.network, e.ref) for e in entry.evidence}
        for item in correction.add_evidence:
            if (item.kind, item.network, item.ref) not in known:
                entry.evidence.append(
                    item.model_copy(update={"found_via": f"{item.found_via} ({label})"})
                )
        entry.sources.append(
            SourceRef(
                name="correction",
                url=correction.source_url,
                retrieved_at=entry.provenance.extracted_at,
                provides=[correction.note or "manual correction"],
            )
        )
    return entries


def load_corrections(event: str) -> list[Correction]:
    path = get_settings().data_dir / "corrections" / f"{event}.yaml"
    if not path.is_file():
        return []
    return TypeAdapter(list[Correction]).validate_python(yaml.safe_load(path.read_text()) or [])


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
    corrections = load_corrections(seed.slug)
    public = apply_corrections(public, corrections)
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
