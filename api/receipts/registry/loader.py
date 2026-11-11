import json
from pathlib import Path
from typing import Any

import psycopg
import yaml
from pydantic import TypeAdapter

from receipts.models.registry import EventSeed, RegistryEntry

_entries = TypeAdapter(list[RegistryEntry])


def read_event_seed(path: Path) -> EventSeed:
    return EventSeed.model_validate(yaml.safe_load(path.read_text()))


def read_registry(path: Path) -> list[RegistryEntry]:
    raw = yaml.safe_load(path.read_text()) or []
    return _entries.validate_python(raw)


def sync_event(conn: psycopg.Connection[Any], seed: EventSeed) -> None:
    conn.execute(
        """
        INSERT INTO events (slug, name, location, window_start, window_end)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (slug) DO UPDATE SET
            name = EXCLUDED.name,
            location = EXCLUDED.location,
            window_start = EXCLUDED.window_start,
            window_end = EXCLUDED.window_end
        """,
        (seed.slug, seed.name, seed.location, seed.window.start, seed.window.end),
    )


def sync_registry(conn: psycopg.Connection[Any], entries: list[RegistryEntry]) -> int:
    for entry in entries:
        _sync_entry(conn, entry)
    return len(entries)


def _sync_entry(conn: psycopg.Connection[Any], entry: RegistryEntry) -> None:
    org = entry.claim.org
    conn.execute(
        """
        INSERT INTO orgs (slug, name, domain, country) VALUES (%s, %s, %s, %s)
        ON CONFLICT (slug) DO UPDATE SET
            name = EXCLUDED.name, domain = EXCLUDED.domain, country = EXCLUDED.country
        """,
        (org.slug, org.name, org.domain, org.country),
    )
    claim, scf, prov = entry.claim, entry.backing.scf, entry.provenance
    conn.execute(
        """
        INSERT INTO claims (
            id, event_slug, org_slug, claim_type, quote, summary, speaker_name, speaker_role,
            video_id, video_url, start_seconds, caption_source,
            scf_found, scf_project_url, scf_awarded_usd,
            extractor_model, extracted_at, confidence, transcript_sha256,
            sources, domain_source, country_source, scf_source
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s,%s)
        ON CONFLICT (id) DO UPDATE SET
            event_slug = EXCLUDED.event_slug, org_slug = EXCLUDED.org_slug,
            claim_type = EXCLUDED.claim_type, quote = EXCLUDED.quote,
            summary = EXCLUDED.summary, speaker_name = EXCLUDED.speaker_name,
            speaker_role = EXCLUDED.speaker_role, video_id = EXCLUDED.video_id,
            video_url = EXCLUDED.video_url, start_seconds = EXCLUDED.start_seconds,
            caption_source = EXCLUDED.caption_source, scf_found = EXCLUDED.scf_found,
            scf_project_url = EXCLUDED.scf_project_url,
            scf_awarded_usd = EXCLUDED.scf_awarded_usd,
            extractor_model = EXCLUDED.extractor_model, extracted_at = EXCLUDED.extracted_at,
            confidence = EXCLUDED.confidence, transcript_sha256 = EXCLUDED.transcript_sha256,
            sources = EXCLUDED.sources, domain_source = EXCLUDED.domain_source,
            country_source = EXCLUDED.country_source, scf_source = EXCLUDED.scf_source
        """,
        (
            entry.id, entry.event, org.slug, claim.type, claim.quote, claim.summary,
            claim.speaker.name, claim.speaker.role, claim.video.id,
            claim.video.url_at_timestamp, claim.video.start_seconds, claim.caption_source,
            scf.found, scf.project_url, scf.awarded_usd,
            prov.extractor_model, prov.extracted_at, prov.confidence, prov.transcript_sha256,
            json.dumps([x.model_dump(mode="json") for x in entry.sources]),
            org.domain_source, org.country_source, scf.source,
        ),
    )  # fmt: skip
    keep: list[tuple[str, str, str]] = []
    for item in entry.evidence:
        conn.execute(
            """
            INSERT INTO evidence (claim_id, kind, network, ref, found_via)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (claim_id, kind, network, ref) DO UPDATE SET found_via = EXCLUDED.found_via
            """,
            (entry.id, item.kind, item.network, item.ref, item.found_via),
        )
        keep.append((item.kind.value, item.network.value, item.ref))
    conn.execute(
        """
        DELETE FROM evidence e
        WHERE e.claim_id = %s
          AND NOT (
              (e.kind::text, e.network::text, e.ref) IN (
                  SELECT * FROM unnest(%s::text[], %s::text[], %s::text[])
              )
          )
        """,
        (entry.id, [k[0] for k in keep], [k[1] for k in keep], [k[2] for k in keep]),
    )
